import json
import requests
import xmltodict
from urllib.parse import urlparse, parse_qs
import time
import re
import os
import yaml
from loguru import logger
from utils import commit_and_push, handle_rate_limit

# Load configuration
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

COMMIT_INTERVAL = config['COMMIT_INTERVAL']
CHUNK_SIZE = config['CHUNK_SIZE']
RATE_LIMIT_THRESHOLD = config['RATE_LIMIT_THRESHOLD']
ARXIV_METADATA_FILE = config['ARXIV_METADATA_FILE']

# Configure logger
logger.add("arxiv_metadata_collector.log", rotation="10 MB")

def extract_arxiv_id(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc == 'arxiv.org':
        path_parts = parsed_url.path.split('/')
        if 'abs' in path_parts or 'pdf' in path_parts:
            # Remove .pdf extension if present
            return path_parts[-1].replace('.pdf', '')
    return None

def fetch_arxiv_metadata(arxiv_id):
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "id_list": arxiv_id,
        "max_results": 1
    }
    response = requests.get(base_url, params=params)
    handle_rate_limit(response, RATE_LIMIT_THRESHOLD)
    if response.status_code == 200:
        data = xmltodict.parse(response.content)
        entry = data['feed']['entry']
        
        # Handle potential variations in author structure
        if isinstance(entry.get('author'), list):
            authors = [author['name'] for author in entry['author']]
        elif isinstance(entry.get('author'), dict):
            authors = [entry['author']['name']]
        else:
            authors = []

        # Handle potential variations in category structure
        if isinstance(entry.get('category'), list):
            categories = [cat['@term'] for cat in entry['category']]
        elif isinstance(entry.get('category'), dict):
            categories = [entry['category']['@term']]
        else:
            categories = []

        return {
            'source': 'arXiv',
            'id': entry['id'],
            'title': entry['title'],
            'authors': authors,
            'abstract': entry['summary'],
            'categories': categories,
            'published': entry['published'],
            'updated': entry['updated']
        }
    return None

def fetch_semantic_scholar_data(identifier, id_type='arxiv'):
    base_url = "https://api.semanticscholar.org/v1/paper/"
    if id_type == 'arxiv':
        url = f"{base_url}arXiv:{identifier}"
    elif id_type == 'doi':
        url = f"{base_url}{identifier}"
    else:  # Search by title and authors
        search_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": identifier,
            "limit": 1
        }
        search_response = requests.get(search_url, params=params)
        handle_rate_limit(search_response, RATE_LIMIT_THRESHOLD)
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data['data']:
                url = f"{base_url}{search_data['data'][0]['paperId']}"
            else:
                return None
        else:
            return None

    response = requests.get(url)
    handle_rate_limit(response, RATE_LIMIT_THRESHOLD)
    if response.status_code == 200:
        data = response.json()
        return {
            'source': 'Semantic Scholar',
            'title': data.get('title'),
            'authors': [author['name'] for author in data.get('authors', [])],
            'abstract': data.get('abstract'),
            'year': data.get('year'),
            'venue': data.get('venue'),
            'url': data.get('url'),
            'doi': data.get('doi'),
            'arxivId': data.get('arxivId'),
            'paperId': data.get('paperId'),
            'citation_count': data.get('citationCount'),
            'influential_citation_count': data.get('influentialCitationCount'),
            'reference_count': data.get('referenceCount')
        }
    return None

def parse_bibtex(bibtex_str):
    fields = {}
    for line in bibtex_str.strip().split('\n')[1:-1]:  # Skip first and last lines
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip().lower()
            value = value.strip().strip(',').strip('{').strip('}').strip()
            fields[key] = value
    return fields

def load_existing_data():
    if os.path.exists(ARXIV_METADATA_FILE):
        with open(ARXIV_METADATA_FILE, 'r') as f:
            return json.load(f)
    return {"last_updated": None, "papers": {}}

def save_data(data):
    with open(ARXIV_METADATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def process_papers(papers, existing_data):
    changes_made = False
    paper_ids = set()

    for i, paper in enumerate(papers):
        if i > 0 and i % CHUNK_SIZE == 0:
            logger.info(f"Processed {i} papers")
            if changes_made:
                save_data(existing_data)
                if i % (CHUNK_SIZE * COMMIT_INTERVAL) == 0:
                    commit_and_push(ARXIV_METADATA_FILE)
                changes_made = False

        arxiv_id = extract_arxiv_id(paper['url'])
        if arxiv_id and arxiv_id not in paper_ids:
            paper_ids.add(arxiv_id)
            if arxiv_id not in existing_data['papers']:
                arxiv_data = fetch_arxiv_metadata(arxiv_id)
                if arxiv_data:
                    semantic_scholar_data = fetch_semantic_scholar_data(arxiv_id, 'arxiv')
                    if semantic_scholar_data:
                        arxiv_data.update(semantic_scholar_data)
                    existing_data['papers'][arxiv_id] = arxiv_data
                    changes_made = True

        if 'bibtex' in paper:
            bibtex_data = parse_bibtex(paper['bibtex'])
            doi = bibtex_data.get('doi')
            title = bibtex_data.get('title')

            if doi and doi not in paper_ids:
                paper_ids.add(doi)
                if doi not in existing_data['papers']:
                    semantic_scholar_data = fetch_semantic_scholar_data(doi, 'doi')
                    if semantic_scholar_data:
                        existing_data['papers'][doi] = semantic_scholar_data
                        existing_data['papers'][doi]['bibtex'] = bibtex_data
                        changes_made = True

            elif title and not any(title.lower() in p['title'].lower() for p in existing_data['papers'].values()):
                identifier = f"{title} {bibtex_data.get('author')}"
                semantic_scholar_data = fetch_semantic_scholar_data(identifier, 'search')
                if semantic_scholar_data:
                    paper_id = semantic_scholar_data['paperId']
                    if paper_id not in existing_data['papers']:
                        existing_data['papers'][paper_id] = semantic_scholar_data
                        existing_data['papers'][paper_id]['bibtex'] = bibtex_data
                        changes_made = True

    if changes_made:
        save_data(existing_data)
        commit_and_push(ARXIV_METADATA_FILE)

    return existing_data

def main():
    existing_data = load_existing_data()

    with open('github_stars.json', 'r') as f:
        github_stars_data = json.load(f)

    papers = []
    for repo_data in github_stars_data['repositories'].values():
        if 'arxiv' in repo_data:
            for url in repo_data['arxiv'].get('urls', []):
                papers.append({'url': url})
            for bibtex in repo_data['arxiv'].get('bibtex_citations', []):
                papers.append({'bibtex': bibtex})

    logger.info(f"Found {len(papers)} papers to process")
    process_papers(papers, existing_data)
    logger.info("arXiv metadata collection completed")

if __name__ == "__main__":
    main()
