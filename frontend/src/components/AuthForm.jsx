import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { FaCloudUploadAlt } from 'react-icons/fa';

const AuthForm = ({ isLogin, onSubmit, error }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    if (isLogin) {
      await onSubmit(formData.email, formData.password);
    } else {
      await onSubmit(formData.username, formData.email, formData.password);
    }
    
    setIsLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <FaCloudUploadAlt size={50} color="#3498db" />
          <h1>{isLogin ? 'Log In' : 'Register'}</h1>
          <p>File Storage Application</p>
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        <form className="auth-form" onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                name="username"
                className="form-control"
                value={formData.username}
                onChange={handleChange}
                required
                minLength={3}
                maxLength={50}
              />
            </div>
          )}
          
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              className="form-control"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              className="form-control"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={8}
            />
          </div>
          
          <button 
            type="submit" 
            className="btn submit-btn"
            disabled={isLoading}
          >
            {isLoading ? 'Processing...' : isLogin ? 'Log In' : 'Register'}
          </button>
        </form>
        
        <div className="auth-footer">
          {isLogin ? (
            <p>Don't have an account? <Link to="/register">Register</Link></p>
          ) : (
            <p>Already have an account? <Link to="/login">Log In</Link></p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthForm;
