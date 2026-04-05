// src/api.js
import axios from 'axios'

const api = axios.create({
  // Updated with your active localtunnel URL
  baseURL: 'https://common-dolls-cough.loca.lt/api', 
  withCredentials: true,
  headers: {
    "Bypass-Tunnel-Reminder": "true" 
  }
})

export default api