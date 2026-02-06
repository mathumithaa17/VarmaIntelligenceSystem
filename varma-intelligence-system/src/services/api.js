import axios from 'axios';
import { API_ENDPOINTS } from '../utils/constants';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5003';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      console.error('Network Error:', error.request);
    } else {
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export const searchSymptoms = async (symptomQuery) => {
  try {
    const response = await apiClient.post(API_ENDPOINTS.SYMPTOM_SEARCH, {
      query: symptomQuery,
    });
    return response.data;
  } catch (error) {
    throw new Error('Failed to search symptoms: ' + error.message);
  }
};

export const queryRAG = async (question, history = []) => {
  try {
    // For RAG, we use the full URL from constants, bypassing the default base URL (5003)
    // Note: We use raw axios here because apiClient has port 5003 baked in.
    const response = await axios.post(API_ENDPOINTS.RAG_QUERY, {
      question: question,
      history: history
    });
    return response.data;
  } catch (error) {
    throw new Error('Failed to query RAG system: ' + error.message);
  }
};

export const getVarmaPoints = async () => {
  try {
    const response = await apiClient.get(API_ENDPOINTS.VARMA_POINTS);
    return response.data;
  } catch (error) {
    throw new Error('Failed to fetch Varma points: ' + error.message);
  }
};

export default apiClient;