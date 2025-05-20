import React, { useState, useRef } from 'react';
import { FaUpload, FaTimes, FaFileUpload } from 'react-icons/fa';
import { uploadFile } from '../services/file';

const FileUpload = ({ folderId, onClose, onFileUploaded }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    if (e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.dataTransfer.files.length > 0) {
      setSelectedFile(e.dataTransfer.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }
    
    try {
      setUploading(true);
      setError(null);
      
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 300);
      
      await uploadFile(selectedFile, folderId);
      
      clearInterval(progressInterval);
      setProgress(100);
      
      setTimeout(() => {
        onFileUploaded();
      }, 500);
    } catch (err) {
      console.error('Error uploading file:', err);
      setError(err.response?.data?.detail || 'Failed to upload file. Please try again.');
      setProgress(0);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <div className="modal-header">
          <h2 className="modal-title">
            <FaUpload /> Upload File
          </h2>
          <button className="modal-close" onClick={onClose} disabled={uploading}>
            <FaTimes />
          </button>
        </div>
        
        <div className="modal-body">
          {error && <div className="error-message">{error}</div>}
          
          <div
            className="upload-area"
            onClick={() => fileInputRef.current.click()}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <FaFileUpload className="upload-icon" />
            <p className="upload-message">
              {selectedFile 
                ? `Selected: ${selectedFile.name} (${(selectedFile.size / 1024).toFixed(2)} KB)` 
                : 'Click or drag file to upload'}
            </p>
            <input
              type="file"
              ref={fileInputRef}
              className="upload-input"
              onChange={handleFileSelect}
              disabled={uploading}
            />
          </div>
          
          {uploading && (
            <div className="upload-progress">
              <p>Uploading: {progress}%</p>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>
        
        <div className="modal-footer">
          <button 
            className="btn btn-secondary" 
            onClick={onClose}
            disabled={uploading}
          >
            Cancel
          </button>
          <button 
            className="btn btn-success" 
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;
