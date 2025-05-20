import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { FaCloudUploadAlt, FaFolderOpen, FaShareAlt, FaSignOutAlt, FaUser } from 'react-icons/fa';

const Navigation = () => {
  const { logout, user } = useAuth();

  return (
    <div className="sidebar">
      <div className="nav-brand">
        <FaCloudUploadAlt />
        <span>Хранилище файлов</span>
      </div>
      
      {user && (
        <div className="user-info">
          <p className="user-greeting">Привет, {user.username}!</p>
          <p className="user-email">{user.email}</p>
          <p className="user-id">
            <FaUser size={12} style={{marginRight: '5px'}} />
            <span className="user-id-label">Твой ID:</span> {user.id}
          </p>
        </div>
      )}
      
      <ul className="nav-items">
        <li className="nav-item">
          <NavLink to="/" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            <FaFolderOpen />
            <span>Мои файлы</span>
          </NavLink>
        </li>
        <li className="nav-item">
          <NavLink to="/shared" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            <FaShareAlt />
            <span>Доступно мне</span>
          </NavLink>
        </li>
      </ul>
      
      <button className="btn logout-btn" onClick={logout}>
        <FaSignOutAlt />
        <span>Выйти</span>
      </button>
    </div>
  );
};

export default Navigation;
