import axios from 'axios';

const api = axios.create({
  baseURL: 'https://bsm-project.onrender.com',
});

export default api;