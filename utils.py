import requests
import subprocess
import time
from loguru import logger

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

def handle_rate_limit(response, threshold):
    remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
    
    if remaining <= threshold:
        current_time = time.time()
        sleep_time = max(reset_time - current_time, 0) + 1
        
        if sleep_time > 0:
            logger.warning(f"Rate limit low. {remaining} requests remaining. Sleeping for {sleep_time:.2f} seconds until reset.")
            time.sleep(sleep_time)
        else:
            logger.info(f"Rate limit low but reset time has passed. Proceeding cautiously.")

def controlled_request(url, method='get', params=None, json=None, max_retries=3, delay=1):
    for attempt in range(max_retries):
        try:
            if method.lower() == 'get':
                response = requests.get(url, params=params)
            elif method.lower() == 'post':
                response = requests.post(url, params=params, json=json)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            time.sleep(delay)  # Wait for 1 second before the next request
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.warning(f"Rate limit exceeded. Retrying in {2**attempt} seconds.")
                time.sleep(2**attempt)  # Exponential backoff
            else:
                raise
    logger.error("Max retries reached. Unable to complete the request.")
    return None
