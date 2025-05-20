import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FaFileDownload, FaExclamationTriangle, FaArrowLeft } from 'react-icons/fa';
import { getPublicFile } from '../services/file';

const PublicFile = () => {
  const { publicKey } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [fileName, setFileName] = useState('');

  useEffect(() => {
    const downloadPublicFile = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const blob = await getPublicFile(publicKey);
        
        // Get filename from Content-Disposition header or use fallback
        const contentDisposition = blob.headers?.get('Content-Disposition');
        let filename = 'downloaded-file';
        
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="(.+)"/);
          if (filenameMatch && filenameMatch[1]) {
            filename = filenameMatch[1];
          }
        }
        
        setFileName(filename);
        
        // Create download link and trigger download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } catch (err) {
        console.error('Error downloading public file:', err);
        setError('Failed to download file. The link may have expired or the file no longer exists.');
      } finally {
        setLoading(false);
      }
    };

    downloadPublicFile();
  }, [publicKey]);

  return (
    <div className="public-file-page">
      <div className="auth-container">
        <div className="auth-card">
          <Link to="/login" className="back-link">
            <FaArrowLeft /> Back to home
          </Link>
          
          <div className="auth-header">
            <FaFileDownload size={50} color="#3498db" />
            <h1>File Download</h1>
          </div>
          
          {loading ? (
            <div className="loading-state">
              <p>Downloading file...</p>
            </div>
          ) : error ? (
            <div className="error-state">
              <FaExclamationTriangle size={30} color="#e74c3c" />
              <p className="error-message">{error}</p>
            </div>
          ) : (
            <div className="success-state">
              <p>File has been downloaded successfully!</p>
              <p>You can now close this page or return to login.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PublicFile;
