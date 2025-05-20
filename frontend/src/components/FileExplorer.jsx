import React, { useState, useEffect } from 'react';
import { FaFolderPlus, FaUpload, FaFolder, FaFile } from 'react-icons/fa';
import FileItem from './FileItem';
import FolderItem from './FolderItem';
import FolderForm from './FolderForm';
import FileUpload from './FileUpload';
import { getFiles, getFolders } from '../services/file';

const FileExplorer = ({ currentFolderId = null, onFolderClick, onRefresh }) => {
  const [files, setFiles] = useState([]);
  const [folders, setFolders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showFolderModal, setShowFolderModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [filesData, foldersData] = await Promise.all([
        getFiles(currentFolderId),
        getFolders(currentFolderId)
      ]);
      
      setFiles(filesData);
      setFolders(foldersData);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load files and folders. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [currentFolderId]);

  const handleRefresh = () => {
    fetchData();
    if (onRefresh) onRefresh();
  };

  const handleFolderCreated = () => {
    setShowFolderModal(false);
    handleRefresh();
  };

  const handleFileUploaded = () => {
    setShowUploadModal(false);
    handleRefresh();
  };

  return (
    <div className="file-explorer">
      <div className="explorer-header">
        <h2 className="explorer-title">Файлы и папки</h2>
        <div className="explorer-actions">
          <button className="btn" onClick={() => setShowFolderModal(true)}>
            <FaFolderPlus /> Новая папка
          </button>
          <button className="btn btn-success" onClick={() => setShowUploadModal(true)}>
            <FaUpload /> Загрузить файл
          </button>
        </div>
      </div>
      
      <div className="explorer-content">
        {loading ? (
          <div className="loading">Loading files and folders...</div>
        ) : error ? (
          <div className="error-message">{error}</div>
        ) : (
          <>
            {folders.length > 0 && (
              <div className="folder-section">
                <h3>Папки</h3>
                <div className="folder-list">
                  {folders.map(folder => (
                    <FolderItem 
                      key={folder.id} 
                      folder={folder} 
                      onClick={() => onFolderClick(folder.id)}
                      onDelete={handleRefresh}
                    />
                  ))}
                </div>
              </div>
            )}
            
            {files.length > 0 ? (
              <div className="file-section">
                <h3>Файлы</h3>
                <div className="file-list">
                  {files.map(file => (
                    <FileItem 
                      key={file.id} 
                      file={file}
                      onDelete={handleRefresh}
                    />
                  ))}
                </div>
              </div>
            ) : (
              folders.length === 0 && (
                <div className="empty-state">
                  <FaFile size={40} />
                  <p>No files or folders found</p>
                  <p>Upload a file or create a folder to get started</p>
                </div>
              )
            )}
          </>
        )}
      </div>
      
      {showFolderModal && (
        <FolderForm 
          parentFolderId={currentFolderId}
          onClose={() => setShowFolderModal(false)}
          onFolderCreated={handleFolderCreated}
        />
      )}
      
      {showUploadModal && (
        <FileUpload 
          folderId={currentFolderId}
          onClose={() => setShowUploadModal(false)}
          onFileUploaded={handleFileUploaded}
        />
      )}
    </div>
  );
};

export default FileExplorer;
