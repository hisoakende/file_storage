import React, { useState } from 'react';
import { FaFile, FaDownload, FaTrash, FaShareAlt, FaLink } from 'react-icons/fa';
import { downloadFile, deleteFile } from '../services/file';
import ShareForm from './ShareForm';
import PublicLink from './PublicLink';

const FileItem = ({ file, onDelete }) => {
  const [showShareModal, setShowShareModal] = useState(false);
  const [showPublicLinkModal, setShowPublicLinkModal] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleDownload = async () => {
    try {
      setLoading(true);
      const blob = await downloadFile(file.id);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = file.original_filename;
      document.body.appendChild(a);
      a.click();
      
      // Clean up
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error downloading file:', err);
      alert('Failed to download file. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm(`Are you sure you want to delete ${file.original_filename}?`)) {
      try {
        setLoading(true);
        await deleteFile(file.id);
        onDelete();
      } catch (err) {
        console.error('Error deleting file:', err);
        alert('Failed to delete file. Please try again.');
      } finally {
        setLoading(false);
      }
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  return (
    <div className="file-item">
      <div className="item-icon">
        <FaFile className="file-icon" size={30} />
      </div>
      <div className="item-name">{file.original_filename}</div>
      <div className="item-meta">
        <div>{formatFileSize(file.size)}</div>
        <div>Added: {formatDate(file.created_at)}</div>
      </div>
      <div className="item-actions">
        <button 
          className="btn action-btn" 
          onClick={handleDownload}
          disabled={loading}
        >
          <FaDownload />
        </button>
        <button 
          className="btn action-btn" 
          onClick={() => setShowShareModal(true)}
          disabled={loading}
        >
          <FaShareAlt />
        </button>
        <button 
          className="btn action-btn" 
          onClick={() => setShowPublicLinkModal(true)}
          disabled={loading}
        >
          <FaLink />
        </button>
        <button 
          className="btn action-btn btn-danger" 
          onClick={handleDelete}
          disabled={loading}
        >
          <FaTrash />
        </button>
      </div>
      
      {showShareModal && (
        <ShareForm 
          itemId={file.id}
          itemType="file"
          onClose={() => setShowShareModal(false)}
        />
      )}
      
      {showPublicLinkModal && (
        <PublicLink 
          fileId={file.id}
          onClose={() => setShowPublicLinkModal(false)}
        />
      )}
    </div>
  );
};

export default FileItem;
