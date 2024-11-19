## Project Structure

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
├── article_metadata_collector.py
├── arxiv_metadata.json
├── arxiv_metadata_collector.py
├── config.yaml
├── docs
│   └── readme
│       ├── base.md.j2
│       └── sections
│           └── main.md.j2
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