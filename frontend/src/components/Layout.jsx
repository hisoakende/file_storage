import React from 'react';
import Navigation from './Navigation';
import { useAuth } from '../contexts/AuthContext';

const Layout = ({ children }) => {
  const { loading } = useAuth();

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="app-layout">
      <Navigation />
      <div className="main-content">
        {children}
      </div>
    </div>
  );
};

export default Layout;
