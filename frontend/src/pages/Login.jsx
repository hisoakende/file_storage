import React from 'react';
import { Navigate } from 'react-router-dom';
import AuthForm from '../components/AuthForm';
import { useAuth } from '../contexts/AuthContext';

const Login = () => {
  const { loginUser, error, isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return (
    <AuthForm 
      isLogin={true} 
      onSubmit={loginUser} 
      error={error} 
    />
  );
};

export default Login;
