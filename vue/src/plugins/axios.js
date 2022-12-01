import axios from 'axios';
import localService from '../services/localService';

const GET_API_URL = () => {
  return process.env.VUE_APP_API_URL;
}

const options = {
  baseURL: GET_API_URL(),
  headers: {
    'Content-Type': 'application/json',
  }
};

const instance = axios.create({ ...options });

instance.interceptors.request.use((config) => {
  const token = localService.getItem('token');
  if (token) {
    config.headers.Authorization = `Basic ${token}`;
  }
  return config;
});

instance.interceptors.response.use((response) => {
  return response;
}, (error) => {
  return Promise.reject(error);
});

export default instance;