import React from 'react';
import { extractArXivId } from '../utils/arxivUtils';

const ExpandedRepoView = ({ repo, name, arxivMetadata }) => {
  const arxivId = extractArXivId(repo.arxiv?.primary_id || repo.arxiv?.primary_url);
  const paperMetadata = arxivMetadata[arxivId];

  return (
    <div className="px-6 py-4 border-t border-gray-100">
      <p className="text-gray-700 mb-2">{repo.metadata.description}</p>
      <p className="text-sm text-gray-600 mb-2">Language: {repo.metadata.language}</p>
      <p className="text-sm text-gray-600 mb-2">Created: {new Date(repo.metadata.created_at).toLocaleDateString()}</p>
      <p className="text-sm text-gray-600 mb-2">Last updated: {new Date(repo.metadata.updated_at).toLocaleDateString()}</p>
      <p className="text-sm text-gray-600 mb-2">Last pushed: {new Date(repo.metadata.pushed_at).toLocaleDateString()}</p>
      <p className="text-sm text-gray-600 mb-2">Starred at: {new Date(repo.metadata.starred_at).toLocaleDateString()}</p>
      {repo.lists && repo.lists.length > 0 && (
        <p className="text-sm text-gray-600 mb-2">Lists: {repo.lists.join(', ')}</p>
      )}
      {paperMetadata && (
        <div className="mt-4">
          <h4 className="text-lg font-semibold mb-2">arXiv Paper Details</h4>
          <p className="text-sm text-gray-700 mb-1">Title: {paperMetadata.title}</p>
          <p className="text-sm text-gray-700 mb-1">Authors: {paperMetadata.authors.join(', ')}</p>
          <p className="text-sm text-gray-700 mb-1">Published: {new Date(paperMetadata.published).toLocaleDateString()}</p>
          <p className="text-sm text-gray-700 mb-1">Last Updated: {new Date(paperMetadata.updated).toLocaleDateString()}</p>
          <p className="text-sm text-gray-700 mb-1">Categories: {paperMetadata.categories.map(cat => cat['@term']).join(', ')}</p>
          <details className="mt-2">
            <summary className="text-sm text-blue-600 cursor-pointer">Abstract</summary>
            <p className="text-sm text-gray-700 mt-1">{paperMetadata.abstract}</p>
          </details>
        </div>
      )}
    </div>
  );
};

export default ExpandedRepoView;
