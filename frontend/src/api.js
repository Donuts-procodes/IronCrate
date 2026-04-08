import axios from 'axios';

const api = axios.create({
  baseURL: '/api',          // Vite proxy forwards /api → http://localhost:5001
  withCredentials: true,    // Required for Flask session cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
