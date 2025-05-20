import api from './api';

// Загрузка файла
export const uploadFile = async (file, folderId = null) => {
  const formData = new FormData();
  formData.append('file', file);
  
  let url = '/files/';
  if (folderId) {
    url += `?folder_id=${folderId}`;
  }
  
  const response = await api.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Получение списка файлов
export const getFiles = async (folderId = null) => {
  let url = '/files/';
  if (folderId) {
    url += `?folder_id=${folderId}`;
  }
  
  const response = await api.get(url);
  return response.data;
};

// Получение файлов, доступных по ссылке
export const getSharedFiles = async () => {
  const response = await api.get('/files/shared');
  return response.data;
};

// Скачивание файла
export const downloadFile = async (fileId) => {
  const response = await api.get(`/files/${fileId}/download`, {
    responseType: 'blob',
  });
  return response.data;
};

// Удаление файла
export const deleteFile = async (fileId) => {
  await api.delete(`/files/${fileId}`);
};

// Создание публичной ссылки
export const createPublicLink = async (fileId, expiresInDays = null) => {
  const data = expiresInDays ? { expires_in_days: expiresInDays } : {};
  const response = await api.post(`/files/${fileId}/public-link`, data);
  return response.data;
};

// Предоставление доступа пользователю
export const shareFile = async (fileId, userId) => {
  const response = await api.post(`/files/${fileId}/share`, { user_id: userId });
  return response.data;
};

// Получение файла по публичной ссылке
export const getPublicFile = async (publicKey) => {
  const response = await api.get(`/files/public/${publicKey}`, {
    responseType: 'blob',
  });
  return response.data;
};

// Получение информации о файле
export const getFileInfo = async (fileId) => {
  const response = await api.get(`/files/${fileId}`);
  return response.data;
};

// Создание папки
export const createFolder = async (name, parentFolderId = null) => {
  const data = { name };
  if (parentFolderId) {
    data.parent_folder_id = parentFolderId;
  }
  
  const response = await api.post('/folders/', data);
  return response.data;
};

// Получение списка папок
export const getFolders = async (parentFolderId = null) => {
  let url = '/folders/';
  if (parentFolderId) {
    url += `?parent_folder_id=${parentFolderId}`;
  }
  
  const response = await api.get(url);
  return response.data;
};

// Удаление папки
export const deleteFolder = async (folderId) => {
  await api.delete(`/folders/${folderId}`);
};

// Предоставление доступа к папке
export const shareFolder = async (folderId, userId) => {
  const response = await api.post(`/folders/${folderId}/share`, { user_id: userId });
  return response.data;
};
