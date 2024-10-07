import React, { useState, useEffect } from 'react';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredRepos, setFilteredRepos] = useState([]);

  useEffect(() => {
    fetch(`${process.env.PUBLIC_URL}/github_stars.json`)
      .then(response => response.json())
      .then(jsonData => setData(jsonData))
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  useEffect(() => {
    if (data && data.repositories) {
      setFilteredRepos(
        Object.entries(data.repositories).filter(([name, repo]) =>
          name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          repo.metadata.description.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }
  }, [searchTerm, data]);

  const getTopTags = () => {
    if (!data || !data.repositories) return [];
    const tagCounts = {};
    Object.values(data.repositories).forEach(repo => {
      repo.lists.forEach(tag => {
        tagCounts[tag] = (tagCounts[tag] || 0) + 1;
      });
    });
    return Object.entries(tagCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);
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
            <h3>{name}</h3>
            <p>{repo.metadata.description}</p>
            <p>Stars: {repo.metadata.stargazers_count}</p>
            <p>Language: {repo.metadata.language}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Dashboard;
