import pytest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the parent directory to the Python path to import the main script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arxiv_metadata_collector import extract_arxiv_id, parse_bibtex, load_existing_data, save_data, fetch_arxiv_metadata, fetch_semantic_scholar_data, process_papers, deduplicate_papers
from utils import controlled_request

def test_extract_arxiv_id():
    assert extract_arxiv_id("https://arxiv.org/abs/1234.56789") == "1234.56789"
    assert extract_arxiv_id("https://arxiv.org/pdf/1234.56789.pdf") == "1234.56789"
    assert extract_arxiv_id("https://example.com") is None

def test_parse_bibtex():
    bibtex = """@article{example2023,
        title={Example Title},
        author={Doe, John and Smith, Jane},
        journal={Example Journal},
        year={2023}
    }"""
    parsed = parse_bibtex(bibtex)
    assert parsed['title'] == 'Example Title'
    assert parsed['author'] == 'Doe, John and Smith, Jane'
    assert parsed['journal'] == 'Example Journal'
    assert parsed['year'] == '2023'

@pytest.fixture
def mock_json_file(tmp_path):
    data = {
        "last_updated": "2023-01-01T00:00:00Z",
        "papers": {
            "1234.56789": {
                "title": "Example Paper",
                "authors": ["John Doe"]
            }
        }
    }
    file = tmp_path / "test_metadata.json"
    file.write_text(json.dumps(data))
    return file

def test_load_existing_data(mock_json_file):
    with patch('arxiv_metadata_collector.ARXIV_METADATA_FILE', str(mock_json_file)):
        data = load_existing_data()
        assert data['last_updated'] == "2023-01-01T00:00:00Z"
        assert '1234.56789' in data['papers']
        assert data['papers']['1234.56789']['title'] == "Example Paper"

def test_save_data(tmp_path):
    test_data = {
        "last_updated": "2023-01-01T00:00:00Z",
        "papers": {
            "1234.56789": {
                "title": "New Paper",
                "authors": ["Jane Smith"]
            }
        }
    }
    file = tmp_path / "test_save.json"
    with patch('arxiv_metadata_collector.ARXIV_METADATA_FILE', str(file)):
        save_data(test_data)
        assert file.exists()
        saved_data = json.loads(file.read_text())
        assert saved_data == test_data

@patch('arxiv_metadata_collector.controlled_request')
def test_fetch_arxiv_metadata(mock_controlled_request):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = """
    <feed>
        <entry>
            <id>http://arxiv.org/abs/1234.56789v1</id>
            <title>Example Title</title>
            <author>
                <name>John Doe</name>
            </author>
            <summary>Example abstract</summary>
            <category term="cs.AI"/>
            <published>2023-01-01T00:00:00Z</published>
            <updated>2023-01-02T00:00:00Z</updated>
        </entry>
    </feed>
    """
    mock_controlled_request.return_value = mock_response

    result = fetch_arxiv_metadata('1234.56789')

    assert result['title'] == 'Example Title'
    assert result['authors'] == ['John Doe']
    assert result['abstract'] == 'Example abstract'
    assert result['categories'] == ['cs.AI']
    assert result['published'] == '2023-01-01T00:00:00Z'
    assert result['updated'] == '2023-01-02T00:00:00Z'

@patch('arxiv_metadata_collector.controlled_request')
def test_fetch_arxiv_metadata_multiple_categories(mock_controlled_request):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = """
    <feed>
        <entry>
            <id>http://arxiv.org/abs/1234.56789v1</id>
            <title>Example Title</title>
            <author>
                <name>John Doe</name>
            </author>
            <summary>Example abstract</summary>
            <category term="cs.AI"/>
            <category term="cs.LG"/>
            <published>2023-01-01T00:00:00Z</published>
            <updated>2023-01-02T00:00:00Z</updated>
        </entry>
    </feed>
    """
    mock_controlled_request.return_value = mock_response

    result = fetch_arxiv_metadata('1234.56789')

    assert result['title'] == 'Example Title'
    assert result['authors'] == ['John Doe']
    assert result['abstract'] == 'Example abstract'
    assert result['categories'] == ['cs.AI', 'cs.LG']
    assert result['published'] == '2023-01-01T00:00:00Z'
    assert result['updated'] == '2023-01-02T00:00:00Z'

@patch('arxiv_metadata_collector.controlled_request')
def test_fetch_semantic_scholar_data(mock_controlled_request):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'title': 'Example Title',
        'authors': [{'name': 'John Doe'}],
        'abstract': 'Example abstract',
        'year': 2023,
        'venue': 'Example Conference',
        'url': 'https://example.com/paper',
        'doi': '10.1234/example',
        'arxivId': '1234.56789',
        'paperId': 'abcdef123456',
        'citationCount': 10,
        'influentialCitationCount': 5,
        'referenceCount': 20
    }
    mock_controlled_request.return_value = mock_response

    result = fetch_semantic_scholar_data('1234.56789', 'arxiv')

    assert result['title'] == 'Example Title'
    assert result['authors'] == ['John Doe']
    assert result['abstract'] == 'Example abstract'
    assert result['year'] == 2023
    assert result['venue'] == 'Example Conference'
    assert result['url'] == 'https://example.com/paper'
    assert result['doi'] == '10.1234/example'
    assert result['arxivId'] == '1234.56789'
    assert result['paperId'] == 'abcdef123456'
    assert result['citation_count'] == 10
    assert result['influential_citation_count'] == 5
    assert result['reference_count'] == 20

@patch('arxiv_metadata_collector.fetch_arxiv_metadata')
@patch('arxiv_metadata_collector.fetch_semantic_scholar_data')
@patch('arxiv_metadata_collector.save_data')
@patch('arxiv_metadata_collector.commit_and_push')
def test_process_papers(mock_commit_and_push, mock_save_data, mock_fetch_semantic_scholar, mock_fetch_arxiv):
    papers = [
        {'url': 'https://arxiv.org/abs/1234.56789'},
        {'bibtex': '@article{example, doi={10.1234/example}, title={Example Title}}'}
    ]
    existing_data = {'papers': {}}

    mock_fetch_arxiv.return_value = {
        'title': 'ArXiv Paper',
        'authors': ['John Doe'],
        'abstract': 'ArXiv abstract'
    }
    mock_fetch_semantic_scholar.return_value = {
        'title': 'Semantic Scholar Paper',
        'authors': ['Jane Smith'],
        'abstract': 'Semantic Scholar abstract'
    }

    result = process_papers(papers, existing_data)

    assert '1234.56789' in result['papers']
    assert '10.1234/example' in result['papers']
    assert result['papers']['1234.56789']['title'] == 'ArXiv Paper'
    assert result['papers']['10.1234/example']['title'] == 'Semantic Scholar Paper'
    assert mock_save_data.call_count > 0
    assert mock_commit_and_push.call_count > 0

def test_deduplicate_papers():
    papers = [
        {'url': 'https://arxiv.org/abs/1234.56789'},
        {'url': 'https://arxiv.org/abs/1234.56789'},  # Duplicate arXiv URL
        {'bibtex': '@article{example1, doi={10.1234/example}, title={Example Title 1}}'},
        {'bibtex': '@article{example2, doi={10.1234/example}, title={Example Title 2}}'},  # Duplicate DOI
        {'bibtex': '@article{example3, title={Unique Title}}'},
        {'bibtex': '@article{example4, title={Unique Title}}'},  # Duplicate title
    ]

    deduplicated = deduplicate_papers(papers)
    
    assert len(deduplicated) == 4  # Should have 4 unique papers
    assert any(p for p in deduplicated if p.get('url') == 'https://arxiv.org/abs/1234.56789')
    assert any(p for p in deduplicated if 'Example Title 1' in p.get('bibtex', ''))
    assert any(p for p in deduplicated if 'Unique Title' in p.get('bibtex', ''))
