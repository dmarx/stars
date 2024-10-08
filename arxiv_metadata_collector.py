import json
import requests
import xmltodict
from urllib.parse import urlparse, parse_qs
import time
import re

def extract_arxiv_id(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc == 'arxiv.org':
        path_parts = parsed_url.path.split('/')
        if 'abs' in path_parts:
            return path_parts[-1]
    return None

def fetch_arxiv_metadata(arxiv_id):
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "id_list": arxiv_id,
        "max_results": 1
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = xmltodict.parse(response.content)
        entry = data['feed']['entry']
        return {
            'source': 'arXiv',
            'id': entry['id'],
            'title': entry['title'],
            'authors': [author['name'] for author in entry['author']],
            'abstract': entry['summary'],
            'categories': entry['category'] if isinstance(entry['category'], list) else [entry['category']],
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
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data['data']:
                url = f"{base_url}{search_data['data'][0]['paperId']}"
            else:
                return None
        else:
            return None

    response = requests.get(url)
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

def main():
    with open('github_stars.json', 'r') as f:
        data = json.load(f)

    metadata = {}
    for repo_name, repo_data in data['repositories'].items():
        if 'arxiv' in repo_data:
            arxiv_urls = repo_data['arxiv'].get('urls', [])
            bibtex_citations = repo_data['arxiv'].get('bibtex_citations', [])

            for url in arxiv_urls:
                arxiv_id = extract_arxiv_id(url)
                if arxiv_id:
                    metadata[url] = fetch_arxiv_metadata(arxiv_id)
                    semantic_scholar_data = fetch_semantic_scholar_data(arxiv_id, 'arxiv')
                    if semantic_scholar_data:
                        metadata[url].update(semantic_scholar_data)
                    time.sleep(3)  # Respect API rate limits

            for bibtex in bibtex_citations:
                bibtex_data = parse_bibtex(bibtex)
                identifier = bibtex_data.get('doi') or f"{bibtex_data.get('title')} {bibtex_data.get('author')}"
                id_type = 'doi' if 'doi' in bibtex_data else 'search'
                semantic_scholar_data = fetch_semantic_scholar_data(identifier, id_type)
                
                if semantic_scholar_data:
                    url = semantic_scholar_data['url']
                    metadata[url] = semantic_scholar_data
                    metadata[url]['bibtex'] = bibtex_data
                    time.sleep(3)  # Respect API rate limits

    with open('comprehensive_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)

if __name__ == "__main__":
    main()
