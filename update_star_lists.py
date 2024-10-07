import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, UTC
import os
from loguru import logger
import sys
import re
import random

GITHUB_API = "https://api.github.com"
GITHUB_URL = "https://github.com"
STARS_FILE = 'github_stars.json'
MAX_RETRIES = 5
INITIAL_BACKOFF = 60  # Initial backoff time in seconds
RATE_LIMIT_THRESHOLD = 10  # Number of requests to keep in reserve
DEFAULT_RATE_LIMIT = 60  # Default to 60 requests per minute
DEFAULT_RATE_LIMIT_WINDOW = 60  # 1 minute in seconds

logger.add("star_lists_update.log", rotation="10 MB")

def load_existing_data():
    if os.path.exists(STARS_FILE):
        with open(STARS_FILE, 'r') as f:
            return json.load(f)
    return {"last_updated": None, "repositories": {}}

def save_data(data):
    with open(STARS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

class RateLimiter:
    def __init__(self, limit=DEFAULT_RATE_LIMIT, window=DEFAULT_RATE_LIMIT_WINDOW):
        self.limit = limit
        self.window = window
        self.tokens = limit
        self.last_updated = time.time()

    def update_rate_limit(self, headers):
        new_limit = int(headers.get('X-RateLimit-Limit', self.limit))
        new_remaining = int(headers.get('X-RateLimit-Remaining', self.tokens))
        new_reset = int(headers.get('X-RateLimit-Reset', time.time() + self.window))
        
        # Only update if we're dealing with API rate limits (which are typically higher)
        if new_limit > DEFAULT_RATE_LIMIT:
            self.limit = new_limit
            self.tokens = new_remaining
            self.window = max(new_reset - time.time(), 1)
        else:
            # For web scraping, stick to the default limits
            self.tokens = min(new_remaining, self.tokens)
        
        self.last_updated = time.time()

    def wait_if_needed(self):
        now = time.time()
        time_passed = now - self.last_updated
        self.tokens = min(self.limit, self.tokens + time_passed * (self.limit / self.window))

        if self.tokens < RATE_LIMIT_THRESHOLD:
            sleep_time = (RATE_LIMIT_THRESHOLD - self.tokens) * (self.window / self.limit)
            logger.info(f"Approaching rate limit. Sleeping for {sleep_time:.2f} seconds.")
            time.sleep(sleep_time)
            self.tokens = RATE_LIMIT_THRESHOLD
            self.last_updated = time.time()
        else:
            self.tokens -= 1
            self.last_updated = now

def exponential_backoff(attempt):
    return INITIAL_BACKOFF * (2 ** attempt) + random.uniform(0, 1)

rate_limiter = RateLimiter()

def make_request(session, url, max_retries=MAX_RETRIES):
    for attempt in range(max_retries):
        rate_limiter.wait_if_needed()
        try:
            response = session.get(url)
            response.raise_for_status()
            rate_limiter.update_rate_limit(response.headers)
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                if attempt < max_retries - 1:
                    backoff_time = exponential_backoff(attempt)
                    logger.warning(f"Rate limited (429). Backing off for {backoff_time:.2f} seconds.")
                    time.sleep(backoff_time)
                    continue
            raise

def get_star_lists(username, session):
    url = f"{GITHUB_URL}/{username}?tab=stars"
    response = make_request(session, url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    lists = []
    list_container = soup.select_one('#profile-lists-container .Box')
    
    if list_container:
        list_items = list_container.select('a.Box-row')
        for item in list_items:
            list_name = item.select_one('h3.f4').text.strip()
            list_url = item['href']
            repo_count_text = item.select_one('div.color-fg-muted').text.strip()
            repo_count = int(re.search(r'\d+', repo_count_text).group())
            lists.append((list_name, list_url, repo_count))
    
    logger.info(f"Found {len(lists)} star lists")
    for name, url, count in lists:
        logger.info(f"List: {name}, URL: {url}, Repositories: {count}")
    
    return lists

def clean_repo_name(repo_name):
    parts = repo_name.split('/')
    if len(parts) == 2:
        owner, name = parts
        return f"{owner.strip()}/{name.strip()}"
    return repo_name.strip()

def get_repos_in_list(list_url, session):
    repos = []
    page = 1
    while True:
        full_url = f"{GITHUB_URL}{list_url}?page={page}"
        try:
            response = make_request(session, full_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            repo_elements = soup.select('#user-list-repositories .col-12.d-block')
            if not repo_elements:
                break
            
            for element in repo_elements:
                repo_link = element.select_one('h3 a')
                if repo_link:
                    repo_name = repo_link.text.strip()
                    clean_name = clean_repo_name(repo_name)
                    repos.append(clean_name)
            
            page += 1
            if page > 100:
                logger.warning(f"Reached page limit (100) for list {list_url}. Some repositories may be missing.")
                break
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Reached end of list or encountered 404 error for {list_url} on page {page}. Some repositories may be missing.")
                break
            else:
                raise
    
    return repos

def commit_and_push():
    try:
        os.system('git config --global user.name "GitHub Action"')
        os.system('git config --global user.email "action@github.com"')
        os.system(f'git add {STARS_FILE}')
        os.system('git commit -m "Update GitHub stars data"')
        os.system('git push')
        logger.info("Changes committed and pushed successfully.")
    except Exception as e:
        logger.error(f"Error during git operations: {e}")

def update_star_lists(username, token):
    logger.info(f"Starting star lists update for user: {username}")
    existing_data = load_existing_data()
    
    session = requests.Session()
    session.headers.update({'Authorization': f'token {token}'})
    
    try:
        api_response = make_request(session, f"{GITHUB_API}/rate_limit")
        rate_limit_data = api_response.json()['resources']['core']
        logger.info(f"Initial rate limit: {rate_limit_data['remaining']}/{rate_limit_data['limit']}")
        
        star_lists = get_star_lists(username, session)
        
        for list_name, list_url, repo_count in star_lists:
            logger.info(f"Processing list: {list_name} (Expected repos: {repo_count})")
            repos_in_list = get_repos_in_list(list_url, session)
            
            logger.info(f"Found {len(repos_in_list)} repositories in list {list_name}")
            if len(repos_in_list) < repo_count:
                logger.warning(f"Found fewer repositories ({len(repos_in_list)}) than expected ({repo_count}) for list {list_name}")
            
            for repo_name in repos_in_list:
                if repo_name in existing_data['repositories']:
                    if list_name not in existing_data['repositories'][repo_name]['lists']:
                        existing_data['repositories'][repo_name]['lists'].append(list_name)
                else:
                    logger.warning(f"Repository {repo_name} found in list but not in existing data")
                    # Optionally, add the repository to existing_data here
            
            existing_data['last_updated'] = datetime.now(UTC).isoformat()
            save_data(existing_data)
            commit_and_push()
            logger.info(f"Completed processing list: {list_name}")
        
        logger.info("Star lists update completed successfully")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred during the update process: {e}")
        existing_data['last_updated'] = datetime.now(UTC).isoformat()
        save_data(existing_data)
        commit_and_push()
        sys.exit(1)

if __name__ == "__main__":
    username = os.environ.get('GITHUB_USERNAME')
    token = os.environ.get('GITHUB_TOKEN')
    
    if not username or not token:
        logger.error("GITHUB_USERNAME or GITHUB_TOKEN environment variable is not set.")
        sys.exit(1)
    
    update_star_lists(username, token)
