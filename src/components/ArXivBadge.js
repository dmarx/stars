import React from 'react';
import { FileText } from 'lucide-react';
import { extractArXivId } from '../utils/arxivUtils';

const ArXivBadge = ({ arxivInfo, arxivMetadata }) => {
  const arxivId = extractArXivId(arxivInfo.primary_id || arxivInfo.primary_url);
  const paperMetadata = arxivMetadata[arxivId];

  return (
    <div className="flex items-center space-x-2">
      <a
        href={`https://arxiv.org/abs/${arxivId}`}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full hover:bg-green-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        onClick={(e) => e.stopPropagation()}
      >
        <FileText size={14} className="mr-1" />
        arXiv
      </a>
      {paperMetadata && paperMetadata.categories && paperMetadata.categories.length > 0 && (
        <span className="text-xs text-gray-500">{paperMetadata.categories[0]['@term']}</span>
      )}
    </div>
  );
};

export default ArXivBadge;
