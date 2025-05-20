import React, { useState } from 'react';
import { FaFolder, FaTrash, FaShareAlt } from 'react-icons/fa';
import { deleteFolder } from '../services/file';
import ShareForm from './ShareForm';

const FolderItem = ({ folder, onClick, onDelete }) => {
  const [showShareModal, setShowShareModal] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleDelete = async (e) => {
    e.stopPropagation(); // Prevent folder navigation
    
    if (window.confirm(`Are you sure you want to delete folder "${folder.name}"? All files inside will also be deleted.`)) {
      try {
        setLoading(true);
        await deleteFolder(folder.id);
        onDelete();
      } catch (err) {
        console.error('Error deleting folder:', err);
        alert('Failed to delete folder. Please try again.');
      } finally {
        setLoading(false);
      }
    }
  };

  const handleShare = (e) => {
    e.stopPropagation(); // Prevent folder navigation
    setShowShareModal(true);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  return (
    <div className="folder-item" onClick={onClick}>
      <div className="item-icon">
        <FaFolder className="folder-icon" size={30} />
      </div>
      <div className="item-name">{folder.name}</div>
      <div className="item-meta">
        <div>Created: {formatDate(folder.created_at)}</div>
      </div>
      <div className="item-actions">
        <button 
          className="btn action-btn" 
          onClick={handleShare}
          disabled={loading}
        >
          <FaShareAlt />
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
          itemId={folder.id}
          itemType="folder"
          onClose={() => setShowShareModal(false)}
        />
      )}
    </div>
  );
};

export default FolderItem;
