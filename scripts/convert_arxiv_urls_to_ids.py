import json
import re
import sys
import subprocess
from loguru import logger

class ArXivURLParsingError(Exception):
    """Custom exception for arXiv URL parsing errors."""
    pass

def extract_arxiv_id(url):
    if url is None:
        return None
    # Regular expression to match arXiv IDs
    pattern = r'arxiv\.org/abs/(\d+\.\d+)'
    match = re.search(pattern, url)
    if not match:
        raise ArXivURLParsingError(f"Unable to extract arXiv ID from URL: {url}")
    return match.group(1)

def convert_arxiv_urls_to_ids(data):
    for repo_name, repo in data['repositories'].items():
        if 'arxiv' in repo:
            if 'urls' in repo['arxiv']:
                #print(f"Processing URLs for repository: {repo_name}", file=sys.stderr)
                arxiv_ids = [extract_arxiv_id(url) for url in repo['arxiv']['urls'] if url is not None]
                repo['arxiv']['ids'] = [id for id in arxiv_ids if id is not None]
                del repo['arxiv']['urls']

            if 'primary_url' in repo['arxiv']:
                #print(f"Processing primary URL for repository: {repo_name}", file=sys.stderr)
                primary_url = repo['arxiv']['primary_url']
                if primary_url is not None:
                    primary_id = extract_arxiv_id(primary_url)
                    if primary_id is not None:
                        repo['arxiv']['primary_id'] = primary_id
                del repo['arxiv']['primary_url']

# Load the JSON file
with open('github_stars.json', 'r') as file:
    data = json.load(file)

# Convert URLs to IDs
convert_arxiv_urls_to_ids(data)

# Save the updated JSON
with open('github_stars_updated.json', 'w') as file:
    json.dump(data, file, indent=2)

print("Conversion complete. Updated data saved to 'github_stars_updated.json'.", file=sys.stderr)

print("Comitting...")

def commit_and_push(file_to_commit):
    try:
        # Configure Git for GitHub Actions
        subprocess.run(["git", "config", "--global", "user.name", "GitHub Action"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "action@github.com"], check=True)
        
        # Check if there are any changes to commit
        status = subprocess.run(["git", "status", "--porcelain", file_to_commit], capture_output=True, text=True, check=True)
        if not status.stdout.strip():
            logger.info(f"No changes to commit for {file_to_commit}.")
            return

        subprocess.run(["git", "add", file_to_commit], check=True)
        subprocess.run(["git", "commit", "-m", f"Update {file_to_commit}"], check=True)
        subprocess.run(["git", "push"], check=True)
        
        logger.info(f"Changes to {file_to_commit} committed and pushed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during git operations: {e}")
        if "nothing to commit" in str(e):
            logger.info("No changes to commit. Continuing execution.")
        else:
            logger.warning("Exiting early due to Git error.")
            raise

commit_and_push('github_stars_updated.json')
