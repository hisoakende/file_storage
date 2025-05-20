import React from 'react';
import { Navigate } from 'react-router-dom';
import AuthForm from '../components/AuthForm';
import { useAuth } from '../contexts/AuthContext';

const Register = () => {
  const { registerUser, error, isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return (
    <AuthForm 
      isLogin={false} 
      onSubmit={registerUser} 
      error={error} 
    />
  );
};

export default Register;
