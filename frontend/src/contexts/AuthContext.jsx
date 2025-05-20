import React, { createContext, useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { getUserInfo, login, register } from '../services/auth';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchUserInfo();
    } else {
      setLoading(false);
    }
  }, []);
  
  const fetchUserInfo = async () => {
    try {
      setLoading(true);
      const userData = await getUserInfo();
      setUser(userData);
      setError(null);
    } catch (err) {
      console.error('Error fetching user info:', err);
      localStorage.removeItem('token');
      setError('Session expired. Please log in again.');
    } finally {
      setLoading(false);
    }
  };
  
  const loginUser = async (email, password) => {
    try {
      setLoading(true);
      setError(null);
      const data = await login(email, password);
      localStorage.setItem('token', data.access_token);
      await fetchUserInfo();
      navigate('/');
      return true;
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
      return false;
    } finally {
      setLoading(false);
    }
  };
  
  const registerUser = async (username, email, password) => {
    try {
      setLoading(true);
      setError(null);
      await register(username, email, password);
      const loginResult = await loginUser(email, password);
      return loginResult;
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
      return false;
    } finally {
      setLoading(false);
    }
  };
  
  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    navigate('/login');
  };
  
  const value = {
    user,
    loading,
    error,
    loginUser,
    registerUser,
    logout,
    isAuthenticated: !!user,
  };
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);
