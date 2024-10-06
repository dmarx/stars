# GitHub Stars Scraper with arXiv and BibTeX Extraction

This repository contains a GitHub Action that automatically scrapes your GitHub stars, even for large collections of over 5000 starred repositories. It organizes them based on your star lists (tags), collects additional metadata for each repository, and includes functionality to extract arXiv URLs and BibTeX citations from README files.

## How it works

1. The GitHub Action runs daily at midnight UTC.
2. It first runs the test suite to ensure all functionalities are working as expected.
3. If tests pass, it executes the `scrape_stars.py` script, which:
   - Performs a backfill process for the initial run or if no existing data is found
   - Conducts incremental updates on subsequent runs
   - Fetches all your starred repositories
   - Retrieves all your star lists
   - Collects additional metadata for each repository
   - Fetches and analyzes the README of each repository
   - Extracts arXiv URLs and BibTeX citations from the README
   - Infers the primary arXiv URL associated with the repository
   - Associates each repository with its corresponding lists, metadata, and extracted information
4. The results are saved in `github_stars.json`
5. If there are changes, the action commits and pushes the updated file to the repository

## Features

- **Automated Testing**: The project includes a comprehensive test suite using pytest to ensure reliability.
- **Logging**: The script uses Loguru for advanced logging capabilities, making debugging and monitoring easier.
- **Backfill Process**: For the initial run or when no existing data is found, the script performs a full backfill of all starred repositories. This process is chunked to manage API rate limits effectively.
- **Incremental Updates**: After the initial backfill, the script performs incremental updates, only fetching new stars and updating metadata for existing repos at specified intervals.
- **Rate Limit Handling**: The script respects GitHub's API rate limits and implements a sleep mechanism when limits are nearly reached.
- **Efficient Data Storage**: The script stores the last update time for each repository, allowing for efficient updates of metadata.
- **arXiv URL Extraction**: The script extracts all arXiv URLs found in the repository's README and description.
- **Primary arXiv URL Inference**: The script attempts to infer which arXiv URL is most likely associated with the repository, based on several heuristics.
- **BibTeX Citation Extraction**: The script extracts any BibTeX citations found in the repository's README.

## Collected Data

For each starred repository, the following information is collected:

- Repository metadata (ID, name, description, URL, etc.)
- Star lists (tags) associated with the repository
- Extracted arXiv URLs from the README and description
- Inferred primary arXiv URL
- Extracted BibTeX citations from the README

## Setup

1. Fork this repository
2. Go to your forked repository's settings
3. Navigate to "Secrets and variables" > "Actions"
4. Add two new repository secrets:
   - `GITHUB_USERNAME`: Your GitHub username
   - `GITHUB_TOKEN`: A GitHub personal access token with `repo` scope
5. The action will now run automatically every day, or you can trigger it manually from the "Actions" tab

## Development

To set up the project for development:

1. Clone the repository
2. Install the required dependencies:
   ```
   pip install requests loguru pytest
   ```
3. Run the tests:
   ```
   pytest
   ```

## Manual Trigger

You can manually trigger the workflow from the "Actions" tab in your GitHub repository.

## Viewing Results

After the action runs successfully, you can view the updated `github_stars.json` file in the repository. This file contains a JSON object with:

- `last_updated`: Timestamp of when the data was last scraped
- `repositories`: An object where each key is a repository name, and the value is another object containing:
  - `lists`: An array of lists (tags) associated with that repository
  - `metadata`: An object containing the collected metadata for the repository
  - `last_updated`: Timestamp of when this repository's data was last updated
  - `arxiv`: An object containing:
    - `urls`: An array of all arXiv URLs found in the README
    - `primary_url`: The inferred primary arXiv URL associated with the repository
    - `bibtex_citations`: An array of BibTeX citations found in the README

## Logs

The script generates a log file `scraper.log` which rotates when it reaches 10 MB. This log file can be useful for debugging and monitoring the scraping process.
