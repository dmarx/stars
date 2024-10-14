import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp, Search, X } from 'lucide-react';

const SortDropdown = ({ sortOption, sortDirection, handleSortChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const options = [
    { value: 'stars', label: 'Stars' },
    { value: 'name', label: 'Name' },
    { value: 'updated_at', label: 'Last Updated' },
    { value: 'created_at', label: 'Created' },
    { value: 'pushed_at', label: 'Last Pushed' },
    { value: 'starred_at', label: 'Starred At' },
  ];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-48 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-100 focus:ring-blue-500"
      >
        {options.find(opt => opt.value === sortOption).label}
        {isOpen ? <ChevronUp className="w-5 h-5 ml-2" /> : <ChevronDown className="w-5 h-5 ml-2" />}
      </button>
      {isOpen && (
        <div className="absolute right-0 w-56 mt-2 origin-top-right bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5">
          <div className="py-1" role="menu" aria-orientation="vertical" aria-labelledby="options-menu">
            {options.map((option) => (
              <button
                key={option.value}
                onClick={() => {
                  handleSortChange(option.value);
                  setIsOpen(false);
                }}
                className="flex items-center justify-between w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                role="menuitem"
              >
                {option.label}
                {sortOption === option.value && (
                  <span>{sortDirection === 'desc' ? '▼' : '▲'}</span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const AdvancedSearch = ({ advancedFilters, setAdvancedFilters }) => {
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setAdvancedFilters(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-4">
        <div>
          <label htmlFor="minStars" className="block text-sm font-medium text-gray-700">Min Stars</label>
          <input
            type="number"
            id="minStars"
            name="minStars"
            value={advancedFilters.minStars}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
          />
        </div>
        <div>
          <label htmlFor="createdAfter" className="block text-sm font-medium text-gray-700">Created After</label>
          <input
            type="date"
            id="createdAfter"
            name="createdAfter"
            value={advancedFilters.createdAfter}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
          />
        </div>
        <div>
          <label htmlFor="createdBefore" className="block text-sm font-medium text-gray-700">Created Before</label>
          <input
            type="date"
            id="createdBefore"
            name="createdBefore"
            value={advancedFilters.createdBefore}
            onChange={handleInputChange}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
          />
        </div>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLists, setSelectedLists] = useState([]);
  const [filteredRepos, setFilteredRepos] = useState([]);
  const [allLists, setAllLists] = useState([]);
  const [expandedRepo, setExpandedRepo] = useState(null);
  const [sortOption, setSortOption] = useState('stars');
  const [sortDirection, setSortDirection] = useState('desc');
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(false);
  const [advancedFilters, setAdvancedFilters] = useState({
    minStars: '',
    createdAfter: '',
    createdBefore: '',
  });

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
      let filtered = Object.entries(data.repositories).filter(([name, repo]) => {
        const matchesSearch = 
          (name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
          ((repo.metadata && repo.metadata.description) || '').toLowerCase().includes(searchTerm.toLowerCase());
        const matchesLists = selectedLists.length === 0 || 
          selectedLists.every(list => repo.lists && repo.lists.includes(list));
        const matchesAdvanced = 
          (!advancedFilters.minStars || repo.metadata.stars >= parseInt(advancedFilters.minStars)) &&
          (!advancedFilters.createdAfter || new Date(repo.metadata.created_at) >= new Date(advancedFilters.createdAfter)) &&
          (!advancedFilters.createdBefore || new Date(repo.metadata.created_at) <= new Date(advancedFilters.createdBefore));
        return matchesSearch && matchesLists && matchesAdvanced;
      });

      filtered.sort((a, b) => {
        const [, repoA] = a;
        const [, repoB] = b;
        const direction = sortDirection === 'desc' ? -1 : 1;

        switch (sortOption) {
          case 'stars':
            return (repoB.metadata.stars - repoA.metadata.stars) * direction;
          case 'name':
            return a[0].localeCompare(b[0]) * direction;
          case 'updated_at':
          case 'created_at':
          case 'pushed_at':
          case 'starred_at':
            return (new Date(repoB.metadata[sortOption]) - new Date(repoA.metadata[sortOption])) * direction;
          default:
            return 0;
        }
      });

      setFilteredRepos(filtered);
    }
  }, [searchTerm, selectedLists, data, sortOption, sortDirection, advancedFilters]);

  const handleSortChange = (option) => {
    if (option === sortOption) {
      setSortDirection(prev => prev === 'desc' ? 'asc' : 'desc');
    } else {
      setSortOption(option);
      setSortDirection('desc');
    }
  };

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
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center mb-4">
            <input
              type="text"
              placeholder="Search repositories..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-grow px-4 py-2 rounded-l-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={() => setShowAdvancedSearch(!showAdvancedSearch)}
              className="px-4 py-2 bg-blue-500 text-white rounded-r-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {showAdvancedSearch ? <X className="w-5 h-5" /> : <Search className="w-5 h-5" />}
            </button>
          </div>
          {showAdvancedSearch && (
            <AdvancedSearch 
              advancedFilters={advancedFilters}
              setAdvancedFilters={setAdvancedFilters}
            />
          )}
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
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold">Repositories ({filteredRepos.length})</h2>
            <SortDropdown 
              sortOption={sortOption}
              sortDirection={sortDirection}
              handleSortChange={handleSortChange}
            />
          </div>
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
                    <p className="text-sm text-gray-600 mb-2">Created: {new Date(repo.metadata.created_at).toLocaleDateString()}</p>
                    <p className="text-sm text-gray-600 mb-2">Last updated: {new Date(repo.metadata.updated_at).toLocaleDateString()}</p>
                    <p className="text-sm text-gray-600 mb-2">Last pushed: {new Date(repo.metadata.pushed_at).toLocaleDateString()}</p>
                    <p className="text-sm text-gray-600 mb-2">Starred at: {new Date(repo.metadata.starred_at).toLocaleDateString()}</p>
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
