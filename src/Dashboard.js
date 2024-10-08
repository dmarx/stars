import React, { useState, useEffect } from 'react';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLists, setSelectedLists] = useState([]);
  const [filteredRepos, setFilteredRepos] = useState([]);
  const [allLists, setAllLists] = useState([]);
  const [expandedRepo, setExpandedRepo] = useState(null);

  useEffect(() => {
    fetch(`${process.env.PUBLIC_URL}/github_stars.json`)
      .then(response => response.json())
      .then(jsonData => {
        setData(jsonData);
        const lists = new Set();
        Object.values(jsonData.repositories).forEach(repo => {
          (repo.lists || []).forEach(list => lists.add(list));
        });
        setAllLists(Array.from(lists).sort());
      })
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  useEffect(() => {
    if (data && data.repositories) {
      setFilteredRepos(
        Object.entries(data.repositories).filter(([name, repo]) => {
          const matchesSearch = 
            (name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
            ((repo.metadata && repo.metadata.description) || '').toLowerCase().includes(searchTerm.toLowerCase());
          const matchesLists = selectedLists.length === 0 || 
            selectedLists.every(list => repo.lists && repo.lists.includes(list));
          return matchesSearch && matchesLists;
        })
      );
    }
  }, [searchTerm, selectedLists, data]);

  const toggleList = (list) => {
    setSelectedLists(prev => 
      prev.includes(list) 
        ? prev.filter(l => l !== list)
        : [...prev, list]
    );
  };

  const toggleRepoExpansion = (name) => {
    setExpandedRepo(expandedRepo === name ? null : name);
  };

  if (!data) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="dashboard">
      <header>
        <h1>GitHub Stars Dashboard</h1>
        <div className="search-container">
          <input
            type="text"
            placeholder="Search repositories..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
      </header>
      
      <aside className="filters">
        <h3>Filter by Lists</h3>
        <div className="list-filters">
          {allLists.map(list => (
            <label key={list} className="list-filter-item">
              <input
                type="checkbox"
                checked={selectedLists.includes(list)}
                onChange={() => toggleList(list)}
              />
              <span>{list}</span>
            </label>
          ))}
        </div>
      </aside>

      <main>
        <h2>Repositories ({filteredRepos.length})</h2>
        <ul className="repo-list">
          {filteredRepos.map(([name, repo]) => (
            <li key={name} className={`repo-item ${expandedRepo === name ? 'expanded' : ''}`}>
              <div className="repo-header" onClick={() => toggleRepoExpansion(name)}>
                <h3>{name}</h3>
                <span className="repo-stars">{repo.metadata && repo.metadata.stars} ★</span>
              </div>
              <div className="repo-details">
                <p>{repo.metadata && repo.metadata.description}</p>
                <p>Language: {repo.metadata && repo.metadata.language}</p>
                {repo.lists && repo.lists.length > 0 && (
                  <p>Lists: {repo.lists.join(', ')}</p>
                )}
                {repo.arxiv && repo.arxiv.primary_url && (
                  <p>
                    arXiv: <a href={repo.arxiv.primary_url} target="_blank" rel="noopener noreferrer">
                      {repo.arxiv.primary_url}
                    </a>
                  </p>
                )}
                <a href={`https://github.com/${name}`} target="_blank" rel="noopener noreferrer" className="repo-link">
                  View on GitHub
                </a>
              </div>
            </li>
          ))}
        </ul>
      </main>
    </div>
  );
};

export default Dashboard;
