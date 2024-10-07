import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, UTC
import os
from loguru import logger
import sys

STARS_FILE = 'github_stars.json'
GITHUB_URL = 'https://github.com'
GITHUB_API_URL = 'https://api.github.com'
DEFAULT_RATE_LIMIT = 60  # Default to 60 requests per minute
DEFAULT_RATE_LIMIT_WINDOW = 60  # 1 minute in seconds
RATE_LIMIT_THRESHOLD = 5  # Number of requests to keep in reserve

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
        limit = int(headers.get('X-RateLimit-Limit', self.limit))
        remaining = int(headers.get('X-RateLimit-Remaining', self.tokens))
        reset = int(headers.get('X-RateLimit-Reset', time.time() + self.window))
        
        self.limit = limit
        self.tokens = remaining
        self.last_updated = time.time()
        self.window = max(reset - self.last_updated, 1)  # Ensure window is at least 1 second

    def wait_if_needed(self):
        now = time.time()
        time_passed = now - self.last_updated
        self.tokens = min(self.limit, self.tokens + time_passed * (self.limit / self.window))

        if self.tokens < 1:
            sleep_time = (1 - self.tokens) * (self.window / self.limit)
            logger.info(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds.")
            time.sleep(sleep_time)
            self.tokens = 1
            self.last_updated = time.time()
        else:
            self.tokens -= 1
            self.last_updated = now

rate_limiter = RateLimiter()

def make_request(session, url):
    rate_limiter.wait_if_needed()
    response = session.get(url)
    response.raise_for_status()
    rate_limiter.update_rate_limit(response.headers)
    return response

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

def get_repos_in_list(list_url, session):
    repos = []
    while list_url:
        response = make_request(session, f"{GITHUB_URL}{list_url}")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        repo_elements = soup.select('h3.wb-break-all')
        for element in repo_elements:
            repo_link = element.find('a')
            if repo_link:
                repo_name = repo_link.text.strip()
                repos.append(repo_name)
        
        next_button = soup.select_one('a.next_page')
        list_url = next_button['href'] if next_button else None
    
    return repos

def update_star_lists(username, token):
    logger.info(f"Starting star lists update for user: {username}")
    existing_data = load_existing_data()
    
    session = requests.Session()
    session.headers.update({'Authorization': f'token {token}'})
    
    try:
        # Make an API request to get accurate rate limit information
        api_response = make_request(session, f"{GITHUB_API_URL}/rate_limit")
        rate_limit_data = api_response.json()['resources']['core']
        rate_limiter.limit = rate_limit_data['limit']
        rate_limiter.tokens = rate_limit_data['remaining']
        rate_limiter.window = rate_limit_data['reset'] - time.time()
        
        star_lists = get_star_lists(username, session)
        
        for list_name, list_url, repo_count in star_lists:
            logger.info(f"Processing list: {list_name} (Expected repos: {repo_count})")
            repos_in_list = get_repos_in_list(list_url, session)
            
            logger.info(f"Found {len(repos_in_list)} repositories in list {list_name}")
            
            for repo_name in repos_in_list:
                if repo_name in existing_data['repositories']:
                    if list_name not in existing_data['repositories'][repo_name]['lists']:
                        existing_data['repositories'][repo_name]['lists'].append(list_name)
                else:
                    logger.warning(f"Repository {repo_name} found in list but not in existing data")
        
        existing_data['last_updated'] = datetime.now(UTC).isoformat()
        save_data(existing_data)
        logger.info("Star lists update completed successfully")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred during the update process: {e}")
        sys.exit(1)

if __name__ == "__main__":
    username = os.environ.get('GITHUB_USERNAME')
    token = os.environ.get('GITHUB_TOKEN')
    
    if not username or not token:
        logger.error("GITHUB_USERNAME or GITHUB_TOKEN environment variable is not set.")
        sys.exit(1)
    
    update_star_lists(username, token)
