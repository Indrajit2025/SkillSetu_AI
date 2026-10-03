import axios from 'axios';

let rawUrl = (import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '/api').trim().replace(/\/+$/, '');

// Ensure /api suffix is attached for FastAPI router endpoints
const API_BASE_URL = (rawUrl === '' || rawUrl === '/api') 
  ? '/api' 
  : (rawUrl.endsWith('/api') ? rawUrl : `${rawUrl}/api`);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT Bearer token if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('skillsetu_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 unauthenticated globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token if invalid or expired
      if (window.location.pathname !== '/login') {
        localStorage.removeItem('skillsetu_token');
        localStorage.removeItem('skillsetu_user');
      }
    }
    return Promise.reject(error);
  }
);

export default api;
