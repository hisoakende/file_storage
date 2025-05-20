import React, { useState } from 'react';
import { FaFolder, FaTimes } from 'react-icons/fa';
import { createFolder } from '../services/file';

const FolderForm = ({ parentFolderId, onClose, onFolderCreated }) => {
  const [folderName, setFolderName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!folderName.trim()) {
      setError('Folder name cannot be empty');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      await createFolder(folderName, parentFolderId);
      onFolderCreated();
    } catch (err) {
      console.error('Error creating folder:', err);
      setError(err.response?.data?.detail || 'Failed to create folder. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <div className="modal-header">
          <h2 className="modal-title">
            <FaFolder /> Create New Folder
          </h2>
          <button className="modal-close" onClick={onClose}>
            <FaTimes />
          </button>
        </div>
        
        <div className="modal-body">
          {error && <div className="error-message">{error}</div>}
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="folderName">Folder Name</label>
              <input
                type="text"
                id="folderName"
                className="form-control"
                value={folderName}
                onChange={(e) => setFolderName(e.target.value)}
                placeholder="Enter folder name"
                required
                autoFocus
                maxLength={255}
              />
            </div>
          </form>
        </div>
        
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose} disabled={loading}>
            Cancel
          </button>
          <button className="btn" onClick={handleSubmit} disabled={loading}>
            {loading ? 'Creating...' : 'Create Folder'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default FolderForm;
