import api from './api';

export const login = async (email, password) => {
  const formData = new FormData();
  formData.append('username', email);  // API ожидает username
  formData.append('password', password);
  
  const response = await api.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response.data;
};

export const register = async (username, email, password) => {
  const response = await api.post('/auth/register', {
    username,
    email,
    password,
  });
  return response.data;
};

export const getUserInfo = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};
