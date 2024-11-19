# GitHub Stars Scraper, Organizer, and Dashboard
This project automatically scrapes and organizes your GitHub stars, including star lists (tags), using GitHub Actions. It also provides a web-based dashboard to explore and search through your starred repositories.

## Features
- Scrapes all starred repositories for a GitHub user
- Retrieves and organizes star lists (tags) for each repository
- Handles large collections (3000+ stars) gracefully
- Implements intelligent rate limiting to avoid API throttling
- Provides detailed logging for transparency and debugging
- Commits and pushes updates only when changes are detected
- Runs daily via GitHub Actions, with option for manual triggers
- Offers a web-based dashboard to explore and search starred repositories

## How it works
1. The GitHub Action runs daily at midnight UTC (or can be manually triggered).
2. It executes two main scripts:
   - `scrape_stars.py`: Fetches all starred repositories and their metadata.
   - `update_star_lists.py`: Retrieves star lists for each repository.
3. The scripts:
   - Fetch all starred repositories and their metadata
   - Retrieve all star lists (tags) for the user
   - Associate each repository with its corresponding lists
   - Extract arXiv URLs and BibTeX citations from README files (when available)
   - Handle rate limiting using both preemptive and reactive strategies
4. Results are saved in `github_stars.json`
5. If there are changes, the action commits and pushes the updated file to the repository
6. A React-based dashboard is built and deployed to GitHub Pages, allowing users to explore their starred repositories

## Setup
1. Fork this repository
2. Go to your forked repository's settings
3. Navigate to "Secrets and variables" > "Actions"
4. Add the following repository secret:
   - `GITHUB_TOKEN`: A GitHub personal access token with `repo` scope
5. The action will now run automatically every day, or you can trigger it manually from the "Actions" tab
6. Enable GitHub Pages in your repository settings, setting the source to the `gh-pages` branch

## File Structure
- `scrape_stars.py`: Main script for fetching starred repositories and metadata
- `update_star_lists.py`: Script for retrieving and organizing star lists
- `.github/workflows/update_stars.yml`: GitHub Actions workflow file for data scraping
- `.github/workflows/deploy-to-gh-pages.yml`: GitHub Actions workflow file for deploying the dashboard
- `github_stars.json`: Output file containing all starred repository data
- `src/`: Directory containing React components for the dashboard
- `public/`: Directory containing public assets for the dashboard

### Front end file structure

```
src/
├── components/
│   ├── Dashboard.js
│   ├── SortDropdown.js
│   ├── AdvancedSearchCondition.js
│   ├── AdvancedSearch.js
│   ├── ArXivBadge.js
│   └── ExpandedRepoView.js
├── hooks/
│   └── useRepositories.js
└── utils/
    ├── arxivUtils.js
    └── sortUtils.js
```

## Dashboard
The dashboard is built using React and Tailwind CSS. It provides the following features:
- Search functionality to find repositories by name or description
- Filtering by star lists (tags)
- Expandable repository cards showing detailed information
- Links to GitHub repositories and associated arXiv papers (when available)

To view the dashboard, visit `https://<your-github-username>.github.io/stars/` after the GitHub Actions workflow has completed.

## Customization
You can customize the behavior of the scripts by modifying the following constants in the Python files:
- `STARS_FILE`: Name of the output JSON file
- `BACKFILL_CHUNK_SIZE`: Number of repositories to process in each backfill chunk
- `COMMIT_INTERVAL`: Number of lists to process before committing changes
- `RATE_LIMIT_THRESHOLD`: Number of API requests to keep in reserve
- `DEFAULT_RATE_LIMIT` and `DEFAULT_RATE_LIMIT_WINDOW`: Default rate limiting for web scraping

You can also customize the dashboard by modifying the React components in the `src/` directory.

## Manual Trigger
You can manually trigger the workflows from the "Actions" tab in your GitHub repository.

## Viewing Results
After the action runs successfully, you can view the updated `github_stars.json` file in the repository. This file contains a JSON object with:
- `last_updated`: Timestamp of when the data was last scraped
- `repositories`: An object where each key is a repository name, and the value is another object containing:
  - `lists`: An array of lists (tags) associated with that repository
  - `metadata`: An object containing the collected metadata for the repository
  - `arxiv`: An object containing arXiv-related information (if available)

You can also explore your starred repositories interactively using the deployed dashboard.

## Limitations
- The script can only retrieve up to 3000 repositories per list due to GitHub's pagination limits.
- Web scraping is used for retrieving star lists, which may break if GitHub significantly changes their HTML structure.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is open source and available under the [MIT License](LICENSE).## Project Structure

```

├── .github
│   └── workflows
│       ├── build_readme.yml
│       ├── collect_article_metadata.yaml
│       ├── collect_arxiv_metadata.yaml
│       ├── convert_arxiv_urls_to_ids.yaml
│       ├── deploy-to-gh-pages.yml
│       ├── fix_arxiv_categories.yaml
│       ├── generate-package-lock.yml
│       ├── generate_summaries.yml
│       ├── main.yml
│       └── update_star_lists.yml
├── .gitignore
├── LICENSE
├── README.md
├── article_metadata_collector.py
├── arxiv_metadata.json
├── arxiv_metadata_collector.py
├── config.yaml
├── docs
│   └── readme
│       ├── base.md.j2
│       └── sections
│           ├── main.md.j2
│           └── structure.md.j2
├── github_stars.json
├── package-lock.json
├── package.json
├── postcss.config.js
├── public
│   ├── github_stars.json
│   └── index.html
├── pyproject.toml
├── scrape_stars.py
├── scripts
│   ├── convert_arxiv_urls_to_ids.py
│   ├── generate-package-lock.js
│   └── transform_categories.py
├── src
│   ├── App.js
│   ├── README.md
│   ├── components
│   │   ├── AdvancedSearch.js
│   │   ├── AdvancedSearchCondition.js
│   │   ├── ArXivBadge.js
│   │   ├── Dashboard.js
│   │   ├── ExpandedRepoView.js
│   │   └── SortDropdown.js
│   ├── hooks
│   │   └── useRepositories.js
│   ├── index.css
│   ├── index.js
│   └── utils
│       ├── arxivUtils.js
│       └── sortUtils.js
├── tailwind.config.js
├── tests
│   ├── __init__.py
│   ├── test_article_metadata_collector.py
│   └── test_scrape.py
├── update_star_lists.py
└── utils.py

```