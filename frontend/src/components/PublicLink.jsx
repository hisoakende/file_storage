import React, { useState } from 'react';
import { FaLink, FaTimes, FaCopy, FaCheck } from 'react-icons/fa';
import { createPublicLink } from '../services/file';

const PublicLink = ({ fileId, onClose }) => {
  const [days, setDays] = useState('7');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [publicLink, setPublicLink] = useState(null);
  const [copied, setCopied] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await createPublicLink(fileId, days ? parseInt(days) : null);
      
      // Format the link for the frontend
      const baseUrl = window.location.origin;
      const fullLink = `${baseUrl}/file/public/${response.public_link.split('/').pop()}`;
      setPublicLink(fullLink);
    } catch (err) {
      console.error('Error creating public link:', err);
      setError(err.response?.data?.detail || 'Failed to create public link. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(publicLink)
      .then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      })
      .catch(err => {
        console.error('Failed to copy link:', err);
      });
  };

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <div className="modal-header">
          <h2 className="modal-title">
            <FaLink /> Create Public Link
          </h2>
          <button className="modal-close" onClick={onClose}>
            <FaTimes />
          </button>
        </div>
        
        <div className="modal-body">
          {error && <div className="error-message">{error}</div>}
          
          {publicLink ? (
            <div className="public-link-result">
              <p>Public link created successfully:</p>
              <div className="link-container">
                <input
                  type="text"
                  className="form-control"
                  value={publicLink}
                  readOnly
                />
                <button 
                  className="btn" 
                  onClick={handleCopy}
                >
                  {copied ? <FaCheck /> : <FaCopy />}
                </button>
              </div>
              <p className="link-expiry">
                {days && parseInt(days) > 0 
                  ? `This link will expire in ${days} days.` 
                  : 'This link will not expire.'}
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="days">Expiration (days)</label>
                <input
                  type="number"
                  id="days"
                  className="form-control"
                  value={days}
                  onChange={(e) => setDays(e.target.value)}
                  placeholder="Leave empty for no expiration"
                  min="0"
                />
                <small className="form-text">
                  Set how many days this link will be valid. Leave empty or set to 0 for no expiration.
                </small>
              </div>
            </form>
          )}
        </div>
        
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose} disabled={loading}>
            Close
          </button>
          {!publicLink && (
            <button className="btn" onClick={handleSubmit} disabled={loading}>
              {loading ? 'Creating...' : 'Create Link'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default PublicLink;
