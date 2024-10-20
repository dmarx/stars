import json
import requests
import xmltodict
from urllib.parse import urlparse, parse_qs
import time
import re
import os
from typing import List, Dict
import yaml
from loguru import logger
from utils import commit_and_push, controlled_request

# Load configuration
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

SEMANTIC_SCHOLAR_BATCH_URL = "https://api.semanticscholar.org/graph/v1/paper/batch"
SEMANTIC_SCHOLAR_FIELDS = "title,authors,abstract,year,venue,url,doi,arxivId,paperId,citationCount,influentialCitationCount,referenceCount"
BATCH_SIZE = 500  # Maximum allowed by the API
COMMIT_INTERVAL = config['COMMIT_INTERVAL']
CHUNK_SIZE = config['CHUNK_SIZE']
#RATE_LIMIT_THRESHOLD = config['RATE_LIMIT_THRESHOLD']
ARXIV_METADATA_FILE = config['ARXIV_METADATA_FILE']

# Configure logger
logger.add("arxiv_metadata_collector.log", rotation="10 MB")

def extract_arxiv_id(url_or_id):
    # Check if it's a URL
    if url_or_id.startswith('http'):
        parsed_url = urlparse(url_or_id)
        if parsed_url.netloc == 'arxiv.org':
            path_parts = parsed_url.path.split('/')
            if 'abs' in path_parts or 'pdf' in path_parts:
                return path_parts[-1].replace('.pdf', '').split('v')[0]  # Remove version number
    else:
        # Check if it's already an arXiv ID
        arxiv_pattern = r'(\d{4}\.\d{4,5})(v\d+)?'
        match = re.search(arxiv_pattern, url_or_id)
        if match:
            return match.group(1)  # Return only the base ID without version
    return None

def parse_bibtex(bibtex_str):
    fields = {}
    # Remove any surrounding whitespace and curly braces
    bibtex_str = bibtex_str.strip().strip('{').strip('}')
    
    # Use regex to find all key-value pairs
    pattern = r'(\w+)\s*=\s*[{"]?((?:[^{"}]|{[^}]*})*)["}]?'
    matches = re.findall(pattern, bibtex_str, re.DOTALL)
    
    for key, value in matches:
        key = key.lower()
        value = value.strip().strip(',').strip('{').strip('}').strip()
        if key == 'doi':
            # Remove any surrounding quotes or braces from the DOI
            value = value.strip('"').strip("'").strip('{').strip('}')
        fields[key] = value
    
    return fields

def extract_identifier(paper):
    if 'url' in paper:
        arxiv_id = extract_arxiv_id(paper['url'])
        if arxiv_id:
            return f"arxiv:{arxiv_id}"
    elif 'bibtex' in paper:
        bibtex_data = parse_bibtex(paper['bibtex'])
        if 'doi' in bibtex_data:
            return f"doi:{bibtex_data['doi']}"
        elif 'arxiv' in bibtex_data:
            arxiv_id = extract_arxiv_id(bibtex_data['arxiv'])
            if arxiv_id:
                return f"arxiv:{arxiv_id}"
        elif 'title' in bibtex_data:
            return f"title:{bibtex_data['title']}"
    return None

def deduplicate_papers(papers):
    unique_papers = []
    seen_identifiers = set()

    for paper in papers:
        identifier = extract_identifier(paper)
        if identifier and identifier not in seen_identifiers:
            unique_papers.append(paper)
            seen_identifiers.add(identifier)

    return unique_papers

def fetch_arxiv_metadata_batch(arxiv_ids):
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "id_list": ",".join(arxiv_ids),
        "max_results": len(arxiv_ids)
    }
    response = controlled_request(base_url, params=params)
    if response and response.status_code == 200:
        data = xmltodict.parse(response.content)
        entries = data['feed'].get('entry', [])
        if not isinstance(entries, list):
            entries = [entries]
        
        results = []
        for entry in entries:
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

            results.append({
                'source': 'arXiv',
                'id': entry['id'],
                'title': entry['title'],
                'authors': authors,
                'abstract': entry['summary'],
                'categories': categories,
                'published': entry['published'],
                'updated': entry['updated']
            })
        return results
    return []

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
        search_response = controlled_request(search_url, params=params)
        if search_response and search_response.status_code == 200:
            search_data = search_response.json()
            if search_data['data']:
                url = f"{base_url}{search_data['data'][0]['paperId']}"
            else:
                return None
        else:
            return None

    response = controlled_request(url)
    if response and response.status_code == 200:
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

def fetch_semantic_scholar_data_batch(identifiers: List[Dict[str, str]]) -> Dict[str, Dict]:
    """
    Fetch data for multiple papers from Semantic Scholar using the batch API.
    
    :param identifiers: List of dictionaries with 'id' and 'id_type' keys
    :return: Dictionary of paper data, keyed by the original identifier
    """
    results = {}
    for i in range(0, len(identifiers), BATCH_SIZE):
        batch = identifiers[i:i+BATCH_SIZE]
        ids = [f"{id_info['id_type']}:{id_info['id']}" for id_info in batch]
        
        response = controlled_request(
            SEMANTIC_SCHOLAR_BATCH_URL,
            method='post',
            params={'fields': SEMANTIC_SCHOLAR_FIELDS},
            json={"ids": ids}
        )
        
        if response and response.status_code == 200:
            batch_results = response.json()
            for paper, id_info in zip(batch_results, batch):
                if paper:  # Check if paper data is not None
                    original_id = f"{id_info['id_type']}:{id_info['id']}"
                    results[original_id] = {
                        'source': 'Semantic Scholar',
                        'title': paper.get('title'),
                        'authors': [author['name'] for author in paper.get('authors', [])],
                        'abstract': paper.get('abstract'),
                        'year': paper.get('year'),
                        'venue': paper.get('venue'),
                        'url': paper.get('url'),
                        'doi': paper.get('doi'),
                        'arxivId': paper.get('arxivId'),
                        'paperId': paper.get('paperId'),
                        'citation_count': paper.get('citationCount'),
                        'influential_citation_count': paper.get('influentialCitationCount'),
                        'reference_count': paper.get('referenceCount')
                    }
    
    return results

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
    semantic_scholar_batch = []

    for paper in papers:
        identifier = extract_identifier(paper)
        if identifier and identifier not in paper_ids:
            paper_ids.add(identifier)
            if identifier not in existing_data['papers']:
                id_type, id_value = identifier.split(':', 1)
                semantic_scholar_batch.append({'id': id_value, 'id_type': id_type})

    if semantic_scholar_batch:
        semantic_scholar_data = fetch_semantic_scholar_data_batch(semantic_scholar_batch)
        for identifier, data in semantic_scholar_data.items():
            if data:
                existing_data['papers'][identifier] = data
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

    logger.info(f"Found {len(papers)} papers before deduplication")
    
    deduplicated_papers = deduplicate_papers(papers)
    logger.info(f"Deduplicated to {len(deduplicated_papers)} unique papers")

    process_papers(deduplicated_papers, existing_data)
    logger.info("arXiv metadata collection completed")

if __name__ == "__main__":
    main()
