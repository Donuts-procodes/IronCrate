// src/api.js
import axios from 'axios'

const api = axios.create({
  // Direct connection to your Flask backend
  baseURL: 'http://localhost:5000/api', 
  withCredentials: true
})

export default api