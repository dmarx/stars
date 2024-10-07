import requests
import json
import os
import re
import sys
import base64
from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta, UTC
import time
from loguru import logger
import subprocess

GITHUB_API = "https://api.github.com"
STARS_FILE = 'github_stars.json'
CHUNK_SIZE = 100
UPDATE_INTERVAL = 7
COMMIT_INTERVAL = 5
CORE_RATE_LIMIT_THRESHOLD = 100
SEARCH_RATE_LIMIT_THRESHOLD = 5

# Configure logger
logger.add("scraper.log", rotation="10 MB")

def check_initial_rate_limit(token):
    url = f"{GITHUB_API}/rate_limit"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    remaining = data['resources']['core']['remaining']
    reset_time = data['resources']['core']['reset']
    
    if remaining <= RATE_LIMIT_THRESHOLD:
        current_time = time.time()
        wait_time = max(reset_time - current_time, 0)
        logger.warning(f"Rate limit is already low ({remaining} remaining). Another process might be running.")
        logger.warning(f"Rate limit will reset in {wait_time:.2f} seconds.")
        logger.warning("Exiting to avoid conflicts.")
        return False
    
    logger.info(f"Initial rate limit check passed. {remaining} requests remaining.")
    return True

def handle_rate_limit(response):
    remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
    
    if remaining <= CORE_RATE_LIMIT_THRESHOLD:
        current_time = time.time()
        sleep_time = max(reset_time - current_time, 0) + 1
        
        if sleep_time > 0:
            logger.warning(f"Rate limit low. {remaining} requests remaining. Sleeping for {sleep_time:.2f} seconds until reset.")
            time.sleep(sleep_time)
        else:
            logger.info(f"Rate limit low but reset time has passed. Proceeding cautiously.")

def get_starred_repos(username, token, since=None):
    url = f"{GITHUB_API}/users/{username}/starred"
    params = {"per_page": 100}
    if since:
        params["since"] = since.isoformat()
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.star+json"
    }
    starred_repos = []
    
    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        handle_rate_limit(response)
        
        starred_repos.extend(response.json())
        url = response.links.get('next', {}).get('url')
        if url:
            params = {}  # Clear params for pagination
    
    return starred_repos

def get_repo_metadata(repo, token):
    url = f"{GITHUB_API}/repos/{repo['full_name']}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        handle_rate_limit(response)
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code in [403, 404]:
            logger.warning(f"{e.response.status_code} error for repo {repo['full_name']}. The repo may be private, deleted, or inaccessible.")
            return None
        raise

def load_existing_data():
    if os.path.exists(STARS_FILE):
        with open(STARS_FILE, 'r') as f:
            return json.load(f)
    return {"last_updated": None, "repositories": {}, "last_processed_index": 0}

def save_data(data):
    with open(STARS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def extract_metadata(metadata, starred_at):
    return {
        'id': metadata['id'],
        'name': metadata['name'],
        'full_name': metadata['full_name'],
        'description': metadata['description'],
        'url': metadata['html_url'],
        'homepage': metadata['homepage'],
        'language': metadata['language'],
        'stars': metadata['stargazers_count'],
        'forks': metadata['forks_count'],
        'open_issues': metadata['open_issues_count'],
        'created_at': metadata['created_at'],
        'updated_at': metadata['updated_at'],
        'pushed_at': metadata['pushed_at'],
        'starred_at': starred_at
    }

def get_readme_content(repo_full_name, token):
    url = f"{GITHUB_API}/repos/{repo_full_name}/readme"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json().get('content', '')
        if content:
            return base64.b64decode(content).decode('utf-8')
    return None

def extract_arxiv_urls(text):
    arxiv_pattern = r'(?:arxiv\.org/(?:abs|pdf)/|arxiv:)(\d{4}\.\d{4,5})'
    return list(OrderedDict.fromkeys(re.findall(arxiv_pattern, text)))

def extract_bibtex(text):
    bibtex_pattern = r'(@\w+\{[^@]*\})'
    return re.findall(bibtex_pattern, text, re.DOTALL)

def infer_primary_arxiv_url(description, readme_content, arxiv_urls):
    if description and arxiv_urls:
        desc_urls = extract_arxiv_urls(description)
        if desc_urls:
            return f"https://arxiv.org/abs/{desc_urls[0]}"
    
    if readme_content:
        # Check for arXiv badge
        badge_pattern = r'\[!\[arXiv\].*\]\(https://arxiv\.org/abs/(\d{4}\.\d{4,5})\)'
        badge_match = re.search(badge_pattern, readme_content)
        if badge_match:
            return f"https://arxiv.org/abs/{badge_match.group(1)}"
    
    if len(arxiv_urls) == 1:
        return f"https://arxiv.org/abs/{arxiv_urls[0]}"
    
    return None

def process_repo(repo_name, repo_data, token):
    readme_content = get_readme_content(repo_name, token)
    
    arxiv_urls = []
    if readme_content:
        arxiv_urls = extract_arxiv_urls(readme_content)
        bibtex_citations = extract_bibtex(readme_content)
    else:
        bibtex_citations = []
    
    description = repo_data['metadata'].get('description', '')
    primary_arxiv_url = infer_primary_arxiv_url(description, readme_content, arxiv_urls)
    
    repo_data['arxiv'] = {
        'urls': [f"https://arxiv.org/abs/{url}" for url in arxiv_urls],
        'primary_url': primary_arxiv_url,
        'bibtex_citations': bibtex_citations
    }
    
    return repo_data

def commit_and_push():
    try:
        subprocess.run(["git", "config", "--global", "user.name", "GitHub Action"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "action@github.com"], check=True)
        subprocess.run(["git", "add", STARS_FILE], check=True)
        subprocess.run(["git", "commit", "-m", "Update GitHub stars data"], check=True)
        subprocess.run(["git", "push"], check=True)
        logger.info("Changes committed and pushed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during git operations: {e}")
        logger.warning("Exiting early due to potential conflict.")
        sys.exit(1)

def process_repo_batch(repos, token, existing_data):
    for item in repos:
        repo_name = item['repo']['full_name']
        if repo_name not in existing_data['repositories']:
            metadata = get_repo_metadata(item['repo'], token)
            if metadata:
                existing_data['repositories'][repo_name] = {
                    'lists': item.get('star_lists', []),
                    'metadata': extract_metadata(metadata, item['starred_at']),
                    'last_updated': datetime.now(UTC).isoformat()
                }
                existing_data['repositories'][repo_name] = process_repo(
                    repo_name, 
                    existing_data['repositories'][repo_name], 
                    token
                )
            else:
                logger.warning(f"Skipping repo {repo_name} due to metadata retrieval failure.")
        else:
            # Update the lists for existing repos
            existing_data['repositories'][repo_name]['lists'] = item.get('star_lists', [])
    return existing_data

def get_git_remote_username():
    try:
        remote_url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"], universal_newlines=True).strip()
        logger.info(f"Git remote URL: {remote_url}")
        
        # Handle different types of URLs:
        # HTTPS: https://github.com/username/repo.git
        # SSH: git@github.com:username/repo.git
        # GitHub Actions: https://github.com/username/repo
        patterns = [
            r"https://github\.com/([^/]+)/",
            r"git@github\.com:([^/]+)/",
            r"https://x-access-token:[^@]+@github\.com/([^/]+)/"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, remote_url)
            if match:
                username = match.group(1)
                logger.info(f"Extracted username: {username}")
                return username
        
        logger.warning(f"Could not extract username from remote URL: {remote_url}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get git remote URL: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in get_git_remote_username: {e}")
    
    return None


def process_stars(username, token, existing_data):
    logger.info("Starting star processing...")
    all_starred = get_starred_repos(username, token)
    total_repos = len(all_starred)
    
    logger.info(f"Found {total_repos} total starred repositories.")

    changes_made = False
    chunks_processed = 0

    for i in range(0, total_repos, CHUNK_SIZE):
        chunk = all_starred[i:i+CHUNK_SIZE]
        logger.info(f"Processing chunk {i//CHUNK_SIZE + 1} of {total_repos//CHUNK_SIZE + 1}")
        
        chunk_changes = False
        
        for item in chunk:
            repo_name = item['repo']['full_name']
            if repo_name not in existing_data['repositories']:
                metadata = get_repo_metadata(item['repo'], token)
                if metadata:
                    existing_data['repositories'][repo_name] = {
                        'lists': item.get('star_lists', []),
                        'metadata': extract_metadata(metadata, item['starred_at']),
                        'last_updated': datetime.now(UTC).isoformat()
                    }
                    existing_data['repositories'][repo_name] = process_repo(
                        repo_name, 
                        existing_data['repositories'][repo_name], 
                        token
                    )
                    chunk_changes = True
                    changes_made = True
                else:
                    logger.warning(f"Skipping repo {repo_name} due to metadata retrieval failure.")
            elif item.get('star_lists', []) != existing_data['repositories'][repo_name]['lists']:
                # Update the lists for existing repos if they've changed
                existing_data['repositories'][repo_name]['lists'] = item.get('star_lists', [])
                chunk_changes = True
                changes_made = True
        
        if chunk_changes:
            existing_data['last_updated'] = datetime.now(UTC).isoformat()
            save_data(existing_data)
            chunks_processed += 1
        
        # Commit and push every COMMIT_INTERVAL chunks with changes
        if chunk_changes and (chunks_processed % COMMIT_INTERVAL == 0):
            commit_and_push()

    # Final commit if there are any uncommitted changes
    if changes_made:
        save_data(existing_data)
        commit_and_push()
    
    logger.info("Star processing completed.")

def main():
    username = os.environ.get('GITHUB_USERNAME') or get_git_remote_username()
    token = os.environ.get('GITHUB_TOKEN')
    
    logger.info(f"Determined username: {username}")
    logger.info(f"Token available: {'Yes' if token else 'No'}")
    
    if not username:
        logger.error("Unable to determine GitHub username. Please set GITHUB_USERNAME environment variable or run from a git repository.")
        raise ValueError("GitHub username must be provided or determinable from git remote.")
    
    if not token:
        logger.error("GITHUB_TOKEN environment variable is not set.")
        raise ValueError("GitHub token must be provided as an environment variable.")
    
    logger.info(f"Using GitHub username: {username}")
    
    # Check initial rate limit
    if not check_initial_rate_limit(token):
        logger.warning("Rate limits are low. Consider rerunning later.")
        # We'll continue anyway, but the warning is logged
    
    existing_data = load_existing_data()
    
    try:
        process_stars(username, token, existing_data)
    except Exception as e:
        logger.error(f"An error occurred during execution: {e}")
        raise

if __name__ == "__main__":
    main()
