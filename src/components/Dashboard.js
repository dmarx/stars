import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredRepos, setFilteredRepos] = useState([]);

  useEffect(() => {
    fetch(`${process.env.PUBLIC_URL}/github_stars.json`)
      .then(response => response.json())
      .then(jsonData => setData(jsonData))
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  useEffect(() => {
    if (data && data.repositories) {
      setFilteredRepos(
        Object.entries(data.repositories).filter(([name, repo]) =>
          name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          repo.metadata.description.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }
  }, [searchTerm, data]);

  const getTopTags = () => {
    if (!data || !data.repositories) return [];
    const tagCounts = {};
    Object.values(data.repositories).forEach(repo => {
      repo.lists.forEach(tag => {
        tagCounts[tag] = (tagCounts[tag] || 0) + 1;
      });
    });
    return Object.entries(tagCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);
  };

  const topTags = getTopTags();

  if (!data || !data.repositories) {
    return <div>Loading...</div>;
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">GitHub Stars Dashboard</h1>
      <Input
        type="text"
        placeholder="Search repositories..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="mb-4"
      />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <Card>
          <CardHeader>
            <CardTitle>Total Repositories</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold">{Object.keys(data.repositories).length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Last Updated</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xl">{new Date(data.last_updated).toLocaleString()}</p>
          </CardContent>
        </Card>
      </div>
      <Card className="mb-4">
        <CardHeader>
          <CardTitle>Top Tags</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topTags}>
              <XAxis dataKey="0" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="1" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredRepos.map(([name, repo]) => (
          <Card key={name}>
            <CardHeader>
              <CardTitle>{name}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-2">{repo.metadata.description}</p>
              <div className="flex flex-wrap gap-2 mb-2">
                {repo.lists.map(tag => (
                  <Badge key={tag} variant="secondary">{tag}</Badge>
                ))}
              </div>
              <p className="text-sm text-gray-500">
                Stars: {repo.metadata.stargazers_count} | 
                Language: {repo.metadata.language}
              </p>
              {repo.arxiv.primary_url && (
                <a href={repo.arxiv.primary_url} className="text-blue-500 hover:underline" target="_blank" rel="noopener noreferrer">
                  arXiv Paper
                </a>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
