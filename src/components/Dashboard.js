import React, { useState } from 'react';
import { Search, SlidersHorizontal, ArrowDown, ArrowUp, ChevronDown, ChevronUp, Github as GithubIcon } from 'lucide-react';
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

  const toggleRepoExpansion = (name, event) => {
    // Prevent toggling if the click was on the GitHub link
    if (event.target.closest('a')) return;
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
                onClick={(e) => toggleRepoExpansion(name, e)}
              >
                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-4">
                    <a
                      href={`https://github.com/${name}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline flex items-center"
                      onClick={(e) => e.stopPropagation()} // Prevent toggling when clicking the link
                    >
                      <GithubIcon size={20} className="mr-1" />
                      {name}
                    </a>
                    <span className="text-sm font-medium text-gray-600">{repo.metadata.stars} ★</span>
                    {repo.arxiv && (repo.arxiv.primary_id || repo.arxiv.primary_url) && (
                      <ArXivBadge arxivInfo={repo.arxiv} arxivMetadata={arxivMetadata} />
                    )}
                  </div>
                  {expandedRepo === name ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                </div>
                <p className="text-sm text-gray-600 mt-2">{repo.metadata.description}</p>
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
