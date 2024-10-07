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
RATE_LIMIT_THRESHOLD = 10  # Number of requests to keep in reserve

logger.add("star_lists_update.log", rotation="10 MB")

def load_existing_data():
    if os.path.exists(STARS_FILE):
        with open(STARS_FILE, 'r') as f:
            return json.load(f)
    return {"last_updated": None, "repositories": {}}

def save_data(data):
    with open(STARS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def handle_rate_limit(response):
    remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
    
    if remaining <= RATE_LIMIT_THRESHOLD:
        current_time = time.time()
        sleep_time = max(reset_time - current_time, 0) + 1
        logger.info(f"Rate limit low. {remaining} requests remaining. Sleeping for {sleep_time:.2f} seconds.")
        time.sleep(sleep_time)

def get_star_lists(username, session):
    url = f"{GITHUB_URL}/{username}?tab=stars"
    response = session.get(url)
    response.raise_for_status()
    handle_rate_limit(response)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    lists = []
    list_elements = soup.select('a[data-hovercard-type="list"]')
    for element in list_elements:
        list_name = element.text.strip()
        list_url = element['href']
        lists.append((list_name, list_url))
    
    return lists

def get_repos_in_list(list_url, session):
    repos = []
    while list_url:
        response = session.get(f"{GITHUB_URL}{list_url}")
        response.raise_for_status()
        handle_rate_limit(response)
        
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
        star_lists = get_star_lists(username, session)
        logger.info(f"Found {len(star_lists)} star lists")
        
        for list_name, list_url in star_lists:
            logger.info(f"Processing list: {list_name}")
            repos_in_list = get_repos_in_list(list_url, session)
            
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
