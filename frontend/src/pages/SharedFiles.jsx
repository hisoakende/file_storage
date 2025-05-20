import React, { useState, useEffect } from 'react';
import { FaShareAlt, FaFile } from 'react-icons/fa';
import FileItem from '../components/FileItem';
import { getSharedFiles } from '../services/file';

const SharedFiles = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSharedFiles = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getSharedFiles();
      setFiles(data);
    } catch (err) {
      console.error('Error fetching shared files:', err);
      setError('Failed to load shared files. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSharedFiles();
  }, []);

  const handleRefresh = () => {
    fetchSharedFiles();
  };

  return (
    <div className="shared-files">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Shared with Me</h1>
      </div>
      
      <div className="file-explorer">
        <div className="explorer-header">
          <h2 className="explorer-title">
            <FaShareAlt /> Files Shared with Me
          </h2>
        </div>
        
        <div className="explorer-content">
          {loading ? (
            <div className="loading">Loading shared files...</div>
          ) : error ? (
            <div className="error-message">{error}</div>
          ) : files.length > 0 ? (
            <div className="file-list">
              {files.map(file => (
                <FileItem 
                  key={file.id} 
                  file={file}
                  onDelete={handleRefresh}
                />
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <FaFile size={40} />
              <p>No shared files found</p>
              <p>Files shared with you will appear here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SharedFiles;
