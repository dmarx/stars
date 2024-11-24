# Python Project Structure

## article_metadata_collector.py
```python
def extract_arxiv_id(url_or_id)

def parse_bibtex(bibtex_str)

def extract_identifier(paper)

def deduplicate_papers(papers)

def fetch_arxiv_metadata_batch(arxiv_ids)

def fetch_semantic_scholar_data(identifier, id_type)

def fetch_semantic_scholar_data_batch(identifiers: List[Dict[[str, str]]]) -> Dict[[str, Dict]]
    """
    Fetch data for multiple papers from Semantic Scholar using the batch API.
    :param identifiers: List of dictionaries with 'id' and 'id_type' keys
    :return: Dictionary of paper data, keyed by the original identifier
    """

def load_existing_data()

def save_data(data)

def process_papers(papers, existing_data)

def main()

```

## arxiv_metadata_collector.py
```python
def clean_arxiv_id(arxiv_id)

def extract_arxiv_id(url_or_id)

def fetch_arxiv_metadata_batch(arxiv_ids)

def load_existing_data()

def save_data(data)

def process_arxiv_ids(arxiv_ids, existing_data)

def main()

```

## scrape_stars.py
```python
def check_initial_rate_limit(token)

def handle_rate_limit(response)

def get_starred_repos(username, token, since)

def get_repo_metadata(repo, token)

def load_existing_data()

def save_data(data)

def extract_metadata(metadata, starred_at)

def get_readme_content(repo_full_name, token)

def extract_arxiv_id(url)

def extract_arxiv_ids(text)

def infer_primary_arxiv_id(description, readme_content, arxiv_ids)

def extract_bibtex(text)

def process_repo(repo_name, repo_data, token)

def process_repo_batch(repos, token, existing_data)

def commit_and_push()

def get_git_remote_username()

def process_stars(username, token, existing_data)

def main()

```

## scripts/convert_arxiv_urls_to_ids.py
```python
class ArXivURLParsingError(Exception)
    """Custom exception for arXiv URL parsing errors."""

def extract_arxiv_id(url)

def convert_arxiv_urls_to_ids(data)

```

## scripts/transform_categories.py
```python
def commit_and_push(file_to_commit)

def transform_categories(data)

def main()

```

## tests/test_article_metadata_collector.py
```python
def test_extract_identifier()

def test_extract_arxiv_id()

def test_parse_bibtex()

def mock_json_file(tmp_path)

def test_load_existing_data(mock_json_file)

def test_save_data(tmp_path)

@patch(...)
def test_fetch_arxiv_metadata(mock_controlled_request)

@patch(...)
def test_fetch_arxiv_metadata_multiple_categories(mock_controlled_request)

@patch(...)
def test_fetch_semantic_scholar_data(mock_controlled_request)

@patch(...)
@patch(...)
@patch(...)
def test_process_papers(mock_commit_and_push, mock_save_data, mock_fetch_semantic_scholar_batch)

def test_deduplicate_papers()

```

## tests/test_scrape.py
```python
def mock_response()

def mock_repo_metadata()

def test_get_starred_repos(mock_response)

def test_get_repo_metadata(mock_response, mock_repo_metadata)

def test_get_repo_metadata_404_error(mock_response)

def test_extract_metadata(mock_repo_metadata)

def test_get_readme_content(mock_response)

def test_extract_arxiv_id()

def test_extract_arxiv_ids()

def test_extract_bibtex()

def test_infer_primary_arxiv_id()

def test_process_repo(repo_data, expected_ids, expected_primary)

def test_handle_rate_limit()

def test_check_initial_rate_limit()

```

## update_star_lists.py
```python
def load_existing_data()

def save_data(data)

class RateLimiter

    def __init__(self, limit, window)

    def update_rate_limit(self, headers)

    def wait_if_needed(self)


def exponential_backoff(attempt)

def make_request(session, url, max_retries)

def get_star_lists(username, session)

def clean_repo_name(repo_name)

def get_repos_in_list(list_url, session)

def commit_and_push()

def update_star_lists(username, token)

```

## utils.py
```python
def commit_and_push(file_to_commit)

def handle_rate_limit(response, threshold)

def controlled_request(url, method, params, json, max_retries, delay)

```
