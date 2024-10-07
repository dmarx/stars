import React, { useState, useEffect } from 'react';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLists, setSelectedLists] = useState([]);
  const [filteredRepos, setFilteredRepos] = useState([]);
  const [allLists, setAllLists] = useState([]);

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

  const getTopTags = () => {
    if (!data || !data.repositories) return [];
    const tagCounts = {};
    Object.values(data.repositories).forEach(repo => {
      (repo.lists || []).forEach(tag => {
        tagCounts[tag] = (tagCounts[tag] || 0) + 1;
      });
    });
    return Object.entries(tagCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);
  };

  const toggleList = (list) => {
    setSelectedLists(prev => 
      prev.includes(list) 
        ? prev.filter(l => l !== list)
        : [...prev, list]
    );
  };

  if (!data) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>GitHub Stars Dashboard</h1>
      <input
        type="text"
        placeholder="Search repositories..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      <div>
        <h3>Filter by Lists:</h3>
        {allLists.map(list => (
          <label key={list}>
            <input
              type="checkbox"
              checked={selectedLists.includes(list)}
              onChange={() => toggleList(list)}
            />
            {list}
          </label>
        ))}
      </div>
      <h2>Top Tags</h2>
      <ul>
        {getTopTags().map(([tag, count]) => (
          <li key={tag}>{tag}: {count}</li>
        ))}
      </ul>
      <h2>Repositories</h2>
      <ul>
        {filteredRepos.map(([name, repo]) => (
          <li key={name}>
            <h3>
              <a href={`https://github.com/${name}`} target="_blank" rel="noopener noreferrer">
                {name}
              </a>
            </h3>
            <p>{repo.metadata && repo.metadata.description}</p>
            <p>Stars: {repo.metadata && repo.metadata.stars}</p>
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
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Dashboard;
