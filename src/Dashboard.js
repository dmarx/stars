import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp, Search, Plus, X, ArrowUp, ArrowDown, SlidersHorizontal } from 'lucide-react';

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

const AdvancedSearchCondition = ({ condition, updateCondition, removeCondition, fieldOptions, allLists }) => {
  const getOperators = (fieldType) => {
    switch (fieldType) {
      case 'string':
        return [
          { value: 'contains', label: 'contains' },
          { value: 'equals', label: 'equals' },
          { value: 'starts_with', label: 'starts with' },
          { value: 'ends_with', label: 'ends with' },
        ];
      case 'number':
        return [
          { value: 'equals', label: 'equals' },
          { value: 'greater_than', label: 'greater than' },
          { value: 'less_than', label: 'less than' },
        ];
      case 'date':
        return [
          { value: 'equals', label: 'equals' },
          { value: 'after', label: 'after' },
          { value: 'before', label: 'before' },
        ];
      case 'list':
        return [
          { value: 'includes', label: 'includes' },
          { value: 'excludes', label: 'excludes' },
        ];
      default:
        return [{ value: 'equals', label: 'equals' }];
    }
  };

  const getInputType = (field) => {
    switch (field) {
      case 'stars':
        return 'number';
      case 'created_at':
      case 'updated_at':
      case 'pushed_at':
      case 'starred_at':
        return 'date';
      case 'lists':
        return 'list';
      default:
        return 'text';
    }
  };

  const renderInput = () => {
    const inputType = getInputType(condition.field);
    switch (inputType) {
      case 'number':
        return (
          <input
            type="number"
            value={condition.value}
            onChange={(e) => updateCondition({ ...condition, value: e.target.value })}
            className="px-2 py-1 border rounded"
          />
        );
      case 'date':
        return (
          <input
            type="date"
            value={condition.value}
            onChange={(e) => updateCondition({ ...condition, value: e.target.value })}
            className="px-2 py-1 border rounded"
          />
        );
      case 'list':
        return (
          <select
            multiple
            value={condition.value.split(',')}
            onChange={(e) => updateCondition({ ...condition, value: Array.from(e.target.selectedOptions, option => option.value).join(',') })}
            className="px-2 py-1 border rounded"
          >
            {allLists.map(list => (
              <option key={list} value={list}>{list}</option>
            ))}
          </select>
        );
      default:
        return (
          <input
            type="text"
            value={condition.value}
            onChange={(e) => updateCondition({ ...condition, value: e.target.value })}
            className="px-2 py-1 border rounded"
          />
        );
    }
  };

  const fieldType = getInputType(condition.field);
  const operators = getOperators(fieldType);

  return (
    <div className="flex items-center space-x-2 mb-2">
      <select
        value={condition.field}
        onChange={(e) => updateCondition({ ...condition, field: e.target.value, operator: getOperators(getInputType(e.target.value))[0].value })}
        className="px-2 py-1 border rounded"
      >
        {fieldOptions.map(option => (
          <option key={option.value} value={option.value}>{option.label}</option>
        ))}
      </select>
      <select
        value={condition.operator}
        onChange={(e) => updateCondition({ ...condition, operator: e.target.value })}
        className="px-2 py-1 border rounded"
      >
        {operators.map(op => (
          <option key={op.value} value={op.value}>{op.label}</option>
        ))}
      </select>
      {renderInput()}
      <button onClick={removeCondition} className="text-red-500"><X size={20} /></button>
    </div>
  );
};

const AdvancedSearch = ({ conditions, setConditions, fieldOptions, allLists }) => {
  const addCondition = () => {
    setConditions([...conditions, { field: 'name', operator: 'contains', value: '', conjunction: 'AND' }]);
  };

  const updateCondition = (index, newCondition) => {
    const newConditions = [...conditions];
    newConditions[index] = newCondition;
    setConditions(newConditions);
  };

  const removeCondition = (index) => {
    setConditions(conditions.filter((_, i) => i !== index));
  };

  return (
    <div className="bg-gray-100 p-4 rounded-lg mb-4">
      <h3 className="text-lg font-semibold mb-2">Advanced Search</h3>
      {conditions.map((condition, index) => (
        <div key={index}>
          <AdvancedSearchCondition
            condition={condition}
            updateCondition={(newCondition) => updateCondition(index, newCondition)}
            removeCondition={() => removeCondition(index)}
            fieldOptions={fieldOptions}
            allLists={allLists}
          />
          {index < conditions.length - 1 && (
            <select
              value={condition.conjunction}
              onChange={(e) => updateCondition(index, { ...condition, conjunction: e.target.value })}
              className="mb-2 px-2 py-1 border rounded"
            >
              <option value="AND">AND</option>
              <option value="OR">OR</option>
            </select>
          )}
        </div>
      ))}
      <button onClick={addCondition} className="flex items-center text-blue-500"><Plus size={20} /> Add condition</button>
    </div>
  );
};

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [filteredRepos, setFilteredRepos] = useState([]);
  const [expandedRepo, setExpandedRepo] = useState(null);
  const [sortOption, setSortOption] = useState('stars');
  const [sortDirection, setSortDirection] = useState('desc');
  const [searchConditions, setSearchConditions] = useState([]);
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(false);
  const [allLists, setAllLists] = useState([]);
  const [textSearch, setTextSearch] = useState('');

  const fieldOptions = [
    { value: 'name', label: 'Name' },
    { value: 'description', label: 'Description' },
    { value: 'language', label: 'Language' },
    { value: 'stars', label: 'Stars' },
    { value: 'created_at', label: 'Created At' },
    { value: 'updated_at', label: 'Updated At' },
    { value: 'pushed_at', label: 'Pushed At' },
    { value: 'starred_at', label: 'Starred At' },
    { value: 'lists', label: 'Lists' },
  ];

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
        const matchesTextSearch = 
          textSearch === '' ||
          name.toLowerCase().includes(textSearch.toLowerCase()) ||
          (repo.metadata.description && repo.metadata.description.toLowerCase().includes(textSearch.toLowerCase()));

        const matchesAdvancedSearch = searchConditions.every((condition, index) => {
          const fieldValue = condition.field === 'name' ? name : 
                             condition.field === 'lists' ? repo.lists :
                             repo.metadata[condition.field];
          let matches;
          switch (condition.operator) {
            case 'contains':
              matches = String(fieldValue).toLowerCase().includes(condition.value.toLowerCase());
              break;
            case 'equals':
              matches = String(fieldValue).toLowerCase() === condition.value.toLowerCase();
              break;
            case 'starts_with':
              matches = String(fieldValue).toLowerCase().startsWith(condition.value.toLowerCase());
              break;
            case 'ends_with':
              matches = String(fieldValue).toLowerCase().endsWith(condition.value.toLowerCase());
              break;
            case 'greater_than':
            case 'after':
              matches = new Date(fieldValue) > new Date(condition.value);
              break;
            case 'less_than':
            case 'before':
              matches = new Date(fieldValue) < new Date(condition.value);
              break;
            case 'includes':
              matches = condition.value.split(',').some(val => repo.lists.includes(val));
              break;
            case 'excludes':
              matches = !condition.value.split(',').some(val => repo.lists.includes(val));
              break;
            default:
              matches = true;
          }
          if (index === 0) return matches;
          return condition.conjunction === 'AND' ? matches : true;
        });

        return matchesTextSearch && matchesAdvancedSearch;
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
  }, [searchConditions, data, sortOption, sortDirection, textSearch]);

  const handleSortChange = (option) => {
    if (option === sortOption) {
      setSortDirection(prev => prev === 'desc' ? 'asc' : 'desc');
    } else {
      setSortOption(option);
      setSortDirection('desc');
    }
  };

  const toggleSortDirection = () => {
    setSortDirection(prev => prev === 'desc' ? 'asc' : 'desc');
  };

  const toggleRepoExpansion = (name) => {
    setExpandedRepo(expandedRepo === name ? null : name);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    // Trigger the search here. In this case, it's already reactive, so we might just want to
    // provide some visual feedback that the search was submitted.
    console.log("Search submitted:", textSearch);
  };

  if (!data) {
    return <div className="flex items-center justify-center h-screen text-2xl">Loading...</div>;
  }

  const ArXivBadge = ({ arxivId }) => (
    <a
      href={`https://arxiv.org/abs/${arxivId}`}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full hover:bg-green-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
      aria-label={`View arXiv paper ${arxivId}`}
    >
      <FileText size={14} className="mr-1" />
      arXiv
    </a>
  );

 return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-center mb-6">GitHub Stars Dashboard</h1>
        <div className="max-w-4xl mx-auto">
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
            />
          )}
        </div>
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
                    {repo.arxiv && repo.arxiv.primary_id && (
                      <ArXivBadge arxivId={repo.arxiv.primary_id} />
                    )}
                  </div>
                  <span className="text-sm font-medium text-gray-600">{repo.metadata && repo.metadata.stars} ★</span>
                </div>
                <p className="text-sm text-gray-600">{repo.metadata && repo.metadata.description}</p>
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
  );
};

export default Dashboard;
