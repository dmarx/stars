import pytest
from unittest.mock import patch, MagicMock
import json
import base64
from datetime import datetime, UTC
import sys
from pathlib import Path
import requests

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scrape_stars import (
    get_starred_repos, get_repo_metadata, extract_metadata,
    get_readme_content, extract_arxiv_id, extract_arxiv_ids,
    extract_bibtex, infer_primary_arxiv_id, process_repo,
    process_stars, handle_rate_limit, check_initial_rate_limit
)

@pytest.fixture
def mock_response():
    mock = MagicMock()
    mock.json.return_value = [{"repo": {"full_name": "test/repo"}}]
    mock.headers = {'X-RateLimit-Remaining': '4000', 'X-RateLimit-Reset': '1600000000'}
    mock.links = {}
    return mock

@pytest.fixture
def mock_repo_metadata():
    return {
        "id": 1,
        "name": "test-repo",
        "full_name": "test/repo",
        "description": "A test repository",
        "html_url": "https://github.com/test/repo",
        "homepage": "https://test.com",
        "language": "Python",
        "stargazers_count": 100,
        "forks_count": 10,
        "open_issues_count": 5,
        "created_at": "2020-01-01T00:00:00Z",
        "updated_at": "2021-01-01T00:00:00Z",
        "pushed_at": "2021-01-01T00:00:00Z",
    }

def test_get_starred_repos(mock_response):
    with patch('scrape_stars.requests.get', return_value=mock_response), \
         patch('scrape_stars.handle_rate_limit'):
        repos = get_starred_repos('testuser', 'testtoken')
    assert repos == [{"repo": {"full_name": "test/repo"}}]

def test_get_repo_metadata(mock_response, mock_repo_metadata):
    mock_response.json.return_value = mock_repo_metadata
    with patch('scrape_stars.requests.get', return_value=mock_response), \
         patch('scrape_stars.handle_rate_limit'):
        metadata = get_repo_metadata({"full_name": "test/repo"}, 'testtoken')
    assert metadata == mock_repo_metadata

def test_get_repo_metadata_404_error(mock_response):
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
    mock_response.status_code = 404
    with patch('scrape_stars.requests.get', return_value=mock_response), \
         patch('scrape_stars.handle_rate_limit'):
        metadata = get_repo_metadata({"full_name": "test/repo"}, 'testtoken')
    assert metadata is None

def test_extract_metadata(mock_repo_metadata):
    starred_at = "2022-01-01T00:00:00Z"
    extracted = extract_metadata(mock_repo_metadata, starred_at)
    assert extracted['id'] == 1
    assert extracted['name'] == "test-repo"
    assert extracted['starred_at'] == starred_at

def test_get_readme_content(mock_response):
    mock_response.status_code = 200
    mock_response.json.return_value = {"content": base64.b64encode(b"Test README").decode('utf-8')}
    with patch('scrape_stars.requests.get', return_value=mock_response):
        content = get_readme_content("test/repo", 'testtoken')
    assert content == "Test README"

def test_extract_arxiv_id():
    assert extract_arxiv_id("https://arxiv.org/abs/2104.08653") == "2104.08653"
    assert extract_arxiv_id("arxiv:2105.14075") == "2105.14075"
    assert extract_arxiv_id("No arXiv ID here") is None

def test_extract_arxiv_ids():
    text = "Check out arxiv.org/abs/2104.08653 and arxiv:2105.14075"
    ids = extract_arxiv_ids(text)
    assert ids == ['2104.08653', '2105.14075']

def test_extract_bibtex():
    text = "@article{test2021, title={Test}, author={Tester}, year={2021}}"
    bibtex = extract_bibtex(text)
    assert bibtex == [text]

def test_infer_primary_arxiv_id():
    description = "Implementation of arxiv:2104.08653"
    readme = "Check out our paper: [arXiv:2105.14075](https://arxiv.org/abs/2105.14075)"
    ids = ['2104.08653', '2105.14075']
    primary = infer_primary_arxiv_id(description, readme, ids)
    assert primary == "2104.08653"

@pytest.mark.parametrize("repo_data,expected_ids,expected_primary", [
    (
        {"metadata": {"description": "arxiv:2104.08653"}},
        ["2104.08653"],
        "2104.08653"
    ),
    (
        {"metadata": {"description": "No arXiv"}},
        [],
        None
    )
])
def test_process_repo(repo_data, expected_ids, expected_primary):
    with patch('scrape_stars.get_readme_content', return_value="arxiv:2104.08653" if expected_ids else ""):
        processed = process_repo("test/repo", repo_data, 'testtoken')
    assert processed['arxiv']['ids'] == expected_ids
    assert processed['arxiv']['primary_id'] == expected_primary

def test_handle_rate_limit():
    mock_response = MagicMock()
    mock_response.headers = {'X-RateLimit-Remaining': '10', 'X-RateLimit-Reset': str(int(datetime.now(UTC).timestamp()) + 3600)}
    with patch('scrape_stars.time.sleep') as mock_sleep:
        handle_rate_limit(mock_response)
        mock_sleep.assert_called()

def test_check_initial_rate_limit():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'resources': {
            'core': {'remaining': 4000, 'reset': int(datetime.now(UTC).timestamp()) + 3600}
        }
    }
    with patch('scrape_stars.requests.get', return_value=mock_response):
        assert check_initial_rate_limit('testtoken') == True

if __name__ == "__main__":
    pytest.main()
