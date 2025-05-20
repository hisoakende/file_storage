import React, { useState } from 'react';
import { FaShareAlt, FaTimes } from 'react-icons/fa';
import { shareFile, shareFolder } from '../services/file';

const ShareForm = ({ itemId, itemType, onClose }) => {
  const [userId, setUserId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!userId.trim()) {
      setError('User ID cannot be empty');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      setSuccess(false);
      
      if (itemType === 'file') {
        await shareFile(itemId, userId);
      } else if (itemType === 'folder') {
        await shareFolder(itemId, userId);
      }
      
      setSuccess(true);
      setUserId('');
    } catch (err) {
      console.error('Error sharing item:', err);
      setError(err.response?.data?.detail || 'Failed to share item. Please check the User ID and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <div className="modal-header">
          <h2 className="modal-title">
            <FaShareAlt /> Share {itemType === 'file' ? 'File' : 'Folder'}
          </h2>
          <button className="modal-close" onClick={onClose}>
            <FaTimes />
          </button>
        </div>
        
        <div className="modal-body">
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">Shared successfully!</div>}
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="userId">User ID</label>
              <input
                type="text"
                id="userId"
                className="form-control"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                placeholder="Enter the user ID to share with"
                required
                autoFocus
              />
              <small className="form-text">
                Enter the ID of the user you want to share this {itemType} with.
              </small>
            </div>
          </form>
        </div>
        
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose} disabled={loading}>
            Close
          </button>
          <button className="btn" onClick={handleSubmit} disabled={loading}>
            {loading ? 'Sharing...' : 'Share'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ShareForm;
