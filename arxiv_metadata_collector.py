import json
import requests
import xmltodict
from urllib.parse import urlparse
import os
import yaml
from loguru import logger
from utils import commit_and_push, controlled_request

# Load configuration
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

COMMIT_INTERVAL = 1 #config['COMMIT_INTERVAL']
CHUNK_SIZE = 1 # config['CHUNK_SIZE']
ARXIV_METADATA_FILE = 'arxiv_metadata.json'
ARXIV_API_BATCH_SIZE = 300 #100  # arXiv API allows up to 100 IDs per request

# Configure logger
logger.add("arxiv_metadata_collector.log", rotation="10 MB")

def extract_arxiv_id(url_or_id):
    if url_or_id.startswith('http'):
        parsed_url = urlparse(url_or_id)
        if parsed_url.netloc == 'arxiv.org':
            path_parts = parsed_url.path.split('/')
            if 'abs' in path_parts or 'pdf' in path_parts:
                return path_parts[-1].replace('.pdf', '').split('v')[0]  # Remove version number
    else:
        # Check if it's already an arXiv ID
        if url_or_id.startswith('arXiv:'):
            url_or_id = url_or_id[6:]
        return url_or_id.split('v')[0]  # Remove version number if present
    return None

def fetch_arxiv_metadata_batch(arxiv_ids):
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "id_list": ','.join(arxiv_ids),
        "max_results": len(arxiv_ids)
    }
    response = controlled_request(base_url, params=params)
    if response and response.status_code == 200:
        data = xmltodict.parse(response.content)
        entries = data['feed']['entry']
        if not isinstance(entries, list):
            entries = [entries]
        
        results = {}
        for entry in entries:
            arxiv_id = entry['id'].split('/abs/')[-1].split('v')[0]
            results[arxiv_id] = {
                'id': entry['id'],
                'title': entry['title'],
                'authors': [author['name'] for author in (entry['author'] if isinstance(entry['author'], list) else [entry['author']])],
                'abstract': entry['summary'],
                'categories': entry['category'] if isinstance(entry['category'], list) else [entry['category']],
                'published': entry['published'],
                'updated': entry['updated'],
                'doi': entry.get('arxiv:doi', {}).get('#text') if 'arxiv:doi' in entry else None
            }
        return results
    return {}

def load_existing_data():
    if os.path.exists(ARXIV_METADATA_FILE):
        with open(ARXIV_METADATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(ARXIV_METADATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def process_arxiv_ids(arxiv_ids, existing_data):
    changes_made = False
    new_arxiv_ids = [id for id in arxiv_ids if id not in existing_data]

    for i in range(0, len(new_arxiv_ids), ARXIV_API_BATCH_SIZE):
        batch = new_arxiv_ids[i:i+ARXIV_API_BATCH_SIZE]
        metadata_batch = fetch_arxiv_metadata_batch(batch)
        
        if metadata_batch:
            existing_data.update(metadata_batch)
            changes_made = True

        if i > 0 and i % CHUNK_SIZE == 0:
            logger.info(f"Processed {i} arXiv IDs")
            if changes_made:
                save_data(existing_data)
                if i % (CHUNK_SIZE * COMMIT_INTERVAL) == 0:
                    commit_and_push(ARXIV_METADATA_FILE)
                changes_made = False

    if changes_made:
        save_data(existing_data)
        commit_and_push(ARXIV_METADATA_FILE)

    return existing_data

def main():
    existing_data = load_existing_data()

    with open('github_stars.json', 'r') as f:
        github_stars_data = json.load(f)

    arxiv_ids = set()
    for repo_data in github_stars_data['repositories'].values():
        if 'arxiv' in repo_data:
            for url in repo_data['arxiv'].get('urls', []):
                arxiv_id = extract_arxiv_id(url)
                if arxiv_id:
                    arxiv_ids.add(arxiv_id)

    logger.info(f"Found {len(arxiv_ids)} unique arXiv IDs")
    
    process_arxiv_ids(list(arxiv_ids), existing_data)
    logger.info("arXiv metadata collection completed")

if __name__ == "__main__":
    main()
