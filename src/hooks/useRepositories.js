import { useState, useEffect } from 'react';
import { getArxivFieldValue } from '../utils/arxivUtils';

const useRepositories = () => {
  const [data, setData] = useState(null);
  const [filteredRepos, setFilteredRepos] = useState([]);
  const [allLists, setAllLists] = useState([]);
  const [arxivMetadata, setArxivMetadata] = useState({});
  const [sortOption, setSortOption] = useState('starred_at');
  const [sortDirection, setSortDirection] = useState('desc');
  const [textSearch, setTextSearch] = useState('');
  const [searchConditions, setSearchConditions] = useState([]);

  useEffect(() => {
    Promise.all([
      fetch(`${process.env.PUBLIC_URL}/github_stars.json`).then(response => response.json()),
      fetch(`${process.env.PUBLIC_URL}/arxiv_metadata.json`).then(response => response.json())
    ])
    .then(([jsonData, metadata]) => {
      setData(jsonData);
      setArxivMetadata(metadata);
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

        const matchesAdvancedSearch = searchConditions.every((condition) => {
          const fieldValue = condition.field === 'name' ? name : 
                             condition.field === 'lists' ? repo.lists || [] :
                             condition.field.startsWith('arxiv_') ? getArxivFieldValue(repo, condition.field, arxivMetadata) :
                             repo.metadata[condition.field];
          
          if (fieldValue === null || fieldValue === undefined) return false;
          let matches;
          switch (condition.operator) {
            case 'contains':
              matches = Array.isArray(fieldValue) 
                ? fieldValue.some(value => String(value).toLowerCase().includes(condition.value.toLowerCase()))
                : String(fieldValue).toLowerCase().includes(condition.value.toLowerCase());
              break;
            case 'equals':
              matches = Array.isArray(fieldValue)
                ? fieldValue.some(value => String(value).toLowerCase() === condition.value.toLowerCase())
                : String(fieldValue).toLowerCase() === condition.value.toLowerCase();
              break;
            case 'starts_with':
              matches = Array.isArray(fieldValue)
                ? fieldValue.some(value => String(value).toLowerCase().startsWith(condition.value.toLowerCase()))
                : String(fieldValue).toLowerCase().startsWith(condition.value.toLowerCase());
              break;
            case 'ends_with':
              matches = Array.isArray(fieldValue)
                ? fieldValue.some(value => String(value).toLowerCase().endsWith(condition.value.toLowerCase()))
                : String(fieldValue).toLowerCase().endsWith(condition.value.toLowerCase());
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
              matches = Array.isArray(fieldValue) && condition.value.split(',').some(val => 
                fieldValue.some(category => category.toLowerCase().includes(val.toLowerCase()))
              );
              break;
            case 'excludes':
              matches = Array.isArray(fieldValue) && !condition.value.split(',').some(val => 
                fieldValue.some(category => category.toLowerCase().includes(val.toLowerCase()))
              );
              break;
            default:
              matches = true;
          }
          return matches;
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
            return (new Date(repoA.metadata[sortOption]) - new Date(repoB.metadata[sortOption])) * direction; // Fixed order
          case 'arxiv_published':
          case 'arxiv_updated':
            const dateA = new Date(getArxivFieldValue(repoA, sortOption, arxivMetadata) || 0);
            const dateB = new Date(getArxivFieldValue(repoB, sortOption, arxivMetadata) || 0);
            return (dateA - dateB) * direction; // Fixed order
          default:
            return 0;
        }
      });

      setFilteredRepos(filtered);
    }
  }, [data, sortOption, sortDirection, textSearch, searchConditions, arxivMetadata]);

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

  return {
    data,
    filteredRepos,
    allLists,
    allCategories: [...new Set(Object.values(arxivMetadata).flatMap(paper => paper.categories))],
    handleSortChange,
    toggleSortDirection,
    arxivMetadata,
    sortOption,
    sortDirection,
    textSearch,
    setTextSearch,
    searchConditions,
    setSearchConditions
  };
};

export default useRepositories;
