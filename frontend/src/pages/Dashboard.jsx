import React, { useState, useEffect } from 'react';
import { FaHome, FaFolder } from 'react-icons/fa';
import FileExplorer from '../components/FileExplorer';
import { getFolders } from '../services/file';

const Dashboard = () => {
  const [currentFolderId, setCurrentFolderId] = useState(null);
  const [breadcrumb, setBreadcrumb] = useState([{ id: null, name: 'Home' }]);
  
  const navigateToFolder = async (folderId) => {
    setCurrentFolderId(folderId);
    
    if (!folderId) {
      // Navigate to root
      setBreadcrumb([{ id: null, name: 'Home' }]);
      return;
    }
    
    // Find folder in current breadcrumb
    const existingIndex = breadcrumb.findIndex(item => item.id === folderId);
    
    if (existingIndex >= 0) {
      // Folder exists in breadcrumb, truncate to this point
      setBreadcrumb(breadcrumb.slice(0, existingIndex + 1));
    } else {
      // Add folder to breadcrumb
      try {
        const folders = await getFolders(breadcrumb[breadcrumb.length - 1].id);
        const folder = folders.find(f => f.id === folderId);
        
        if (folder) {
          setBreadcrumb([...breadcrumb, { id: folder.id, name: folder.name }]);
        }
      } catch (err) {
        console.error('Error updating breadcrumb:', err);
      }
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Дашборд</h1>
      </div>
      
      <nav aria-label="breadcrumb">
        <ol className="breadcrumb">
          {breadcrumb.map((item, index) => (
            <li 
              key={index} 
              className={`breadcrumb-item ${index === breadcrumb.length - 1 ? 'active' : ''}`}
            >
              {index === breadcrumb.length - 1 ? (
                <span>
                  <FaFolder /> {item.name}
                </span>
              ) : (
                <a href="#" onClick={() => navigateToFolder(item.id)}>
                  {index === 0 ? <FaHome /> : <FaFolder />} {item.name}
                </a>
              )}
            </li>
          ))}
        </ol>
      </nav>
      
      <FileExplorer 
        currentFolderId={currentFolderId}
        onFolderClick={navigateToFolder}
      />
    </div>
  );
};

export default Dashboard;
