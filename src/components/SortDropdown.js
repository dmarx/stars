import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

const SortDropdown = ({ sortOption, sortDirection, handleSortChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const options = [
    { value: 'stars', label: 'Stars' },
    { value: 'name', label: 'Name' },
    { value: 'updated_at', label: 'Last Updated' },
    { value: 'created_at', label: 'Created' },
    { value: 'pushed_at', label: 'Last Pushed' },
    { value: 'starred_at', label: 'Starred At' },
    { value: 'arxiv_published', label: 'arXiv Published Date' },
    { value: 'arxiv_updated', label: 'arXiv Updated Date' },
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

export default SortDropdown;
