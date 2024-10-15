import json
import os
import yaml
from loguru import logger
import arxiv
from utils import commit_and_push

# Load configuration
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

COMMIT_INTERVAL = config['COMMIT_INTERVAL']
CHUNK_SIZE = config['CHUNK_SIZE']
ARXIV_METADATA_FILE = 'arxiv_metadata.json'
ARXIV_API_BATCH_SIZE = 100  # arxiv package default is 100 results per query

# Configure logger
logger.add("arxiv_metadata_collector.log", rotation="10 MB")

def extract_arxiv_id(url_or_id):
    if url_or_id.startswith('http'):
        # Extract ID from URL
        return url_or_id.split('/')[-1].split('v')[0]
    else:
        # Remove 'arXiv:' prefix if present and version number
        return url_or_id.replace('arXiv:', '').split('v')[0]

def fetch_arxiv_metadata_batch(arxiv_ids):
    client = arxiv.Client()
    search = arxiv.Search(
        id_list=arxiv_ids,
        max_results=len(arxiv_ids)
    )
    
    results = {}
    for result in client.results(search):
        arxiv_id = result.get_short_id()
        results[arxiv_id] = {
            'id': result.entry_id,
            'title': result.title,
            'authors': [author.name for author in result.authors],
            'abstract': result.summary,
            'categories': [category['@term'] for category in result.categories],
            'published': result.published.isoformat(),
            'updated': result.updated.isoformat(),
            'doi': result.doi,
            'comment': result.comment,
            'journal_ref': result.journal_ref,
            'primary_category': result.primary_category
        }
    return results

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
