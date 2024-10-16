export const extractArXivId = (idOrUrl) => {
  if (!idOrUrl) return null;
  if (!idOrUrl.includes('/')) return idOrUrl;
  const match = idOrUrl.match(/\/(\d+\.\d+)/);
  return match ? match[1] : null;
};

export const getArxivFieldValue = (repo, field, arxivMetadata) => {
  const arxivId = extractArXivId(repo.arxiv?.primary_id || repo.arxiv?.primary_url);
  const paperMetadata = arxivMetadata[arxivId];
  if (!paperMetadata) return null;

  switch (field) {
    case 'arxiv_category':
      return paperMetadata.categories || [];
    case 'arxiv_published':
      return paperMetadata.published || null;
    case 'arxiv_updated':
      return paperMetadata.updated || null;
    case 'arxiv_primary':
      return arxivId ? 'yes' : 'no';
    default:
      return null;
  }
};
