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
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(false);

  const {
    data,
    filteredRepos,
    allLists,
    allCategories,
    handleSortChange,
    toggleSortDirection,
    arxivMetadata,
    sortOption,
    sortDirection,
    textSearch,
    setTextSearch,
    searchConditions,
    setSearchConditions
  } = useRepositories();

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
        <form onSubmit={handleSearchSubmit} className="flex items-center mb-4">
          <input
            type="text"
            placeholder="Search repositories..."
            value={textSearch}
            onChange={(e) => setTextSearch(e.target.value)}
            className="flex-grow px-4 py-2 rounded-l-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded-r-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Search"
          >
            <Search size={20} />
          </button>
        </form>
        <div className="flex justify-between items-center mb-4">
          <button
            onClick={() => setShowAdvancedSearch(!showAdvancedSearch)}
            className="flex items-center px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <SlidersHorizontal size={20} className="mr-2" />
            {showAdvancedSearch ? 'Hide' : 'Show'} Advanced Search
          </button>
          <div className="flex items-center space-x-2">
            <SortDropdown 
              sortOption={sortOption}
              sortDirection={sortDirection}
              handleSortChange={handleSortChange}
            />
            <button
              onClick={toggleSortDirection}
              className="p-2 bg-gray-200 rounded-full hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label={`Sort ${sortDirection === 'desc' ? 'descending' : 'ascending'}`}
            >
              {sortDirection === 'desc' ? <ArrowDown size={20} /> : <ArrowUp size={20} />}
            </button>
          </div>
        </div>
        {showAdvancedSearch && (
          <AdvancedSearch 
            conditions={searchConditions}
            setConditions={setSearchConditions}
            fieldOptions={fieldOptions}
            allLists={allLists}
            allCategories={allCategories}
          />
        )}
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
                      <ArXivBadge arxivInfo={repo.arxiv} arxivMetadata={arxivMetadata} />
                    )}
                  </div>
                  <span className="text-sm font-medium text-gray-600">{repo.metadata.stars} ★</span>
                </div>
                <p className="text-sm text-gray-600">{repo.metadata.description}</p>
              </div>
              {expandedRepo === name && (
                <ExpandedRepoView repo={repo} name={name} arxivMetadata={arxivMetadata} />
              )}
            </li>
          ))}
        </ul>
      </main>
    </div>
  );
};

export default Dashboard;
