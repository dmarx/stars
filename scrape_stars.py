import requests
import json
import os
import re
import base64
from collections import defaultdict
from datetime import datetime, timedelta
import time
from loguru import logger

GITHUB_API = "https://api.github.com"
STARS_FILE = 'github_stars.json'
BACKFILL_CHUNK_SIZE = 100
UPDATE_INTERVAL = 7

# Configure logger
logger.add("scraper.log", rotation="10 MB")

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
        starred_repos.extend(response.json())
        url = response.links.get('next', {}).get('url')
        if url:
            params = {}  # Clear params for pagination
        
        # Respect rate limit
        if int(response.headers['X-RateLimit-Remaining']) < 10:
            reset_time = int(response.headers['X-RateLimit-Reset'])
            sleep_time = max(reset_time - time.time(), 0) + 1
            logger.warning(f"Rate limit nearly exceeded. Sleeping for {sleep_time} seconds.")
            time.sleep(sleep_time)
    
    return starred_repos

def get_repo_metadata(repo, token):
    url = f"{GITHUB_API}/repos/{repo['full_name']}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    # Respect rate limit
    if int(response.headers['X-RateLimit-Remaining']) < 10:
        reset_time = int(response.headers['X-RateLimit-Reset'])
        sleep_time = max(reset_time - time.time(), 0) + 1
        logger.warning(f"Rate limit nearly exceeded. Sleeping for {sleep_time} seconds.")
        time.sleep(sleep_time)
    
    return response.json()

def load_existing_data():
    if os.path.exists(STARS_FILE):
        with open(STARS_FILE, 'r') as f:
            return json.load(f)
    return {"last_updated": None, "repositories": {}}

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
    return re.findall(arxiv_pattern, text)

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

def backfill_stars(username, token, existing_data):
    logger.info("Starting backfill process...")
    all_starred = get_starred_repos(username, token)
    total_repos = len(all_starred)
    
    for i in range(0, total_repos, BACKFILL_CHUNK_SIZE):
        chunk = all_starred[i:i+BACKFILL_CHUNK_SIZE]
        logger.info(f"Processing chunk {i//BACKFILL_CHUNK_SIZE + 1} of {total_repos//BACKFILL_CHUNK_SIZE + 1}")
        
        for item in chunk:
            repo_name = item['repo']['full_name']
            if repo_name not in existing_data['repositories'] or \
               'metadata' not in existing_data['repositories'][repo_name]:
                metadata = get_repo_metadata(item['repo'], token)
                existing_data['repositories'][repo_name] = {
                    'lists': item.get('star_lists', []),
                    'metadata': extract_metadata(metadata, item['starred_at']),
                    'last_updated': datetime.utcnow().isoformat()
                }
            
            existing_data['repositories'][repo_name] = process_repo(
                repo_name, 
                existing_data['repositories'][repo_name], 
                token
            )
        
        existing_data['last_updated'] = datetime.utcnow().isoformat()
        save_data(existing_data)
    
    logger.info("Backfill process completed.")

def update_stars(username, token, existing_data):
    logger.info("Starting incremental update process...")
    last_updated = datetime.fromisoformat(existing_data['last_updated']) if existing_data['last_updated'] else None
    new_stars = get_starred_repos(username, token, since=last_updated)
    
    update_cutoff = datetime.utcnow() - timedelta(days=UPDATE_INTERVAL)
    
    for item in new_stars:
        repo_name = item['repo']['full_name']
        metadata = get_repo_metadata(item['repo'], token)
        existing_data['repositories'][repo_name] = {
            'lists': item.get('star_lists', []),
            'metadata': extract_metadata(metadata, item['starred_at']),
            'last_updated': datetime.utcnow().isoformat()
        }
        existing_data['repositories'][repo_name] = process_repo(
            repo_name, 
            existing_data['repositories'][repo_name], 
            token
        )
    
    # Update metadata and arXiv info for existing repos if necessary
    for repo_name, repo_data in existing_data['repositories'].items():
        if 'last_updated' not in repo_data or \
           datetime.fromisoformat(repo_data['last_updated']) < update_cutoff:
            logger.info(f"Updating metadata and arXiv info for {repo_name}")
            metadata = get_repo_metadata({'full_name': repo_name}, token)
            repo_data['metadata'] = extract_metadata(metadata, repo_data['metadata']['starred_at'])
            repo_data['last_updated'] = datetime.utcnow().isoformat()
            existing_data['repositories'][repo_name] = process_repo(repo_name, repo_data, token)
    
    existing_data['last_updated'] = datetime.utcnow().isoformat()
    save_data(existing_data)
    logger.info("Incremental update process completed.")

def get_git_remote_username():
    try:
        remote_url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"], universal_newlines=True).strip()
        # Extract username from URLs like:
        # https://github.com/username/repo.git
        # git@github.com:username/repo.git
        match = re.search(r"[/:]([^/]+)/[^/]+\.git$", remote_url)
        if match:
            return match.group(1)
    except subprocess.CalledProcessError:
        logger.warning("Failed to get git remote URL. Ensure you're in a git repository.")
    return None


def main():
    username = os.environ.get('GITHUB_USERNAME') or get_git_remote_username()
    token = os.environ.get('GITHUB_TOKEN')
    
    if not username:
        logger.error("Unable to determine GitHub username. Please set GITHUB_USERNAME environment variable or run from a git repository.")
        raise ValueError("GitHub username must be provided or determinable from git remote.")
    
    if not token:
        logger.error("GITHUB_TOKEN environment variable is not set.")
        raise ValueError("GitHub token must be provided as an environment variable.")
    
    logger.info(f"Using GitHub username: {username}")
    
    existing_data = load_existing_data()
    
    try:
        if not existing_data['last_updated']:
            backfill_stars(username, token, existing_data)
        else:
            update_stars(username, token, existing_data)
    except Exception as e:
        logger.error(f"An error occurred during execution: {e}")
        raise

if __name__ == "__main__":
    main()
