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
    return <div className="flex items-center justify-center h-screen text-2xl">Loading...</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-center mb-6">GitHub Stars Dashboard</h1>
        <div className="max-w-2xl mx-auto">
          <input
            type="text"
            placeholder="Search repositories..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </header>
      
      <div className="flex flex-col md:flex-row gap-8">
        <aside className="md:w-1/4">
          <h3 className="text-xl font-semibold mb-4">Filter by Lists</h3>
          <div className="space-y-2">
            {allLists.map(list => (
              <label key={list} className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedLists.includes(list)}
                  onChange={() => toggleList(list)}
                  className="mr-2"
                />
                <span>{list}</span>
              </label>
            ))}
          </div>
        </aside>

        <main className="md:w-3/4">
          <h2 className="text-2xl font-semibold mb-4">Repositories ({filteredRepos.length})</h2>
          <ul className="space-y-4">
            {filteredRepos.map(([name, repo]) => (
              <li key={name} className="bg-white shadow rounded-lg overflow-hidden">
                <div 
                  className="px-6 py-4 cursor-pointer hover:bg-gray-50"
                  onClick={() => toggleRepoExpansion(name)}
                >
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-blue-600">{name}</h3>
                    <span className="text-sm font-medium text-gray-600">{repo.metadata && repo.metadata.stars} ★</span>
                  </div>
                </div>
                {expandedRepo === name && (
                  <div className="px-6 py-4 border-t border-gray-100">
                    <p className="text-gray-700 mb-2">{repo.metadata && repo.metadata.description}</p>
                    <p className="text-sm text-gray-600 mb-2">Language: {repo.metadata && repo.metadata.language}</p>
                    {repo.lists && repo.lists.length > 0 && (
                      <p className="text-sm text-gray-600 mb-2">Lists: {repo.lists.join(', ')}</p>
                    )}
                    {repo.arxiv && repo.arxiv.primary_id && (
                      <p className="text-sm mb-2">
                        Primary arXiv: <a href={`https://arxiv.org/abs/${repo.arxiv.primary_id}`} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                          {repo.arxiv.primary_id}
                        </a>
                      </p>
                    )}
                    {repo.arxiv && repo.arxiv.ids && repo.arxiv.ids.length > 0 && (
                      <p className="text-sm mb-2">
                        All arXiv IDs: {repo.arxiv.ids.map(id => (
                          <a key={id} href={`https://arxiv.org/abs/${id}`} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline mr-2">
                            {id}
                          </a>
                        ))}
                      </p>
                    )}
                    <a 
                      href={`https://github.com/${name}`} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="inline-block mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition duration-200"
                    >
                      View on GitHub
                    </a>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
