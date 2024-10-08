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
    <div style={{ fontFamily: 'Arial, sans-serif', maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <h1 style={{ textAlign: 'center' }}>GitHub Stars Dashboard</h1>
      <input
        type="text"
        placeholder="Search repositories..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        style={{ width: '100%', padding: '10px', marginBottom: '20px' }}
      />
      <div style={{ marginBottom: '20px' }}>
        <h3>Filter by Lists:</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
          {allLists.map(list => (
            <label key={list} style={{ display: 'flex', alignItems: 'center', marginRight: '10px' }}>
              <input
                type="checkbox"
                checked={selectedLists.includes(list)}
                onChange={() => toggleList(list)}
                style={{ marginRight: '5px' }}
              />
              {list}
            </label>
          ))}
        </div>
      </div>
      <h2>Repositories ({filteredRepos.length})</h2>
      <ul style={{ listStyleType: 'none', padding: 0 }}>
        {filteredRepos.map(([name, repo]) => (
          <li key={name} style={{ marginBottom: '20px', borderBottom: '1px solid #ccc', paddingBottom: '10px' }}>
            <h3>
              <a href={`https://github.com/${name}`} target="_blank" rel="noopener noreferrer" style={{ color: '#0366d6', textDecoration: 'none' }}>
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
                arXiv: <a href={repo.arxiv.primary_url} target="_blank" rel="noopener noreferrer" style={{ color: '#0366d6' }}>
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
