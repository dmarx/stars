import React, { useState } from 'react';
import { Search, SlidersHorizontal, ArrowDown, ArrowUp } from 'lucide-react';
import SortDropdown from './SortDropdown';
import AdvancedSearch from './AdvancedSearch';
import ArXivBadge from './ArXivBadge';
import ExpandedRepoView from './ExpandedRepoView';
import useRepositories from '../hooks/useRepositories';
import { fieldOptions } from '../utils/sortUtils';

const Dashboard = () => {
  const [expandedRepo, setExpandedRepo] = useState(null);
  const [sortOption, setSortOption] = useState('stars');
  const [sortDirection, setSortDirection] = useState('desc');
  const [searchConditions, setSearchConditions] = useState([]);
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(false);
  const [textSearch, setTextSearch] = useState('');

  const {
    data,
    filteredRepos,
    allLists,
    allCategories,
    handleSortChange,
    toggleSortDirection,
  } = useRepositories(sortOption, sortDirection, textSearch, searchConditions);

  const toggleRepoExpansion = (name) => {
    setExpandedRepo(expandedRepo === name ? null : name);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    console.log("Search submitted:", textSearch);
  };

  if (!data) {
    return <div className="flex items-center justify-center h-screen text-2xl">Loading...</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8">
        {/* Header content */}
      </header>
      
      <main>
        <h2 className="text-2xl font-semibold mb-4">Repositories ({filteredRepos.length})</h2>
        <ul className="space-y-4">
          {filteredRepos.map(([name, repo]) => (
            <li key={name} className="bg-white shadow rounded-lg overflow-hidden">
              <div 
                className="px-6 py-4 cursor-pointer hover:bg-gray-50"
                onClick={() => toggleRepoExpansion(name)}
              >
                <div className="flex justify-between items-center mb-2">
                  <div className="flex items-center space-x-2">
                    <h3 className="text-lg font-semibold text-blue-600">{name}</h3>
                    {repo.arxiv && (repo.arxiv.primary_id || repo.arxiv.primary_url) && (
                      <ArXivBadge arxivInfo={repo.arxiv} />
                    )}
                  </div>
                  <span className="text-sm font-medium text-gray-600">{repo.metadata.stars} ★</span>
                </div>
                <p className="text-sm text-gray-600">{repo.metadata.description}</p>
              </div>
              {expandedRepo === name && (
                <ExpandedRepoView repo={repo} name={name} />
              )}
            </li>
          ))}
        </ul>
      </main>
    </div>
  );
};

export default Dashboard;
