import axios from 'axios';

const api = axios.create({
  baseURL: 'https://bsm-project.onrender.com',
  withCredentials: true
});

api.interceptors.request.use(request => {
  console.log('Starting Request', request);
  return request;
});

export default api;