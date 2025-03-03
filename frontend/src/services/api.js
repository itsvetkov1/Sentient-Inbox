import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

// Create axios instance
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add authentication interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Authentication services
export const authService = {
  login: async (email, password) => {
    try {
      const response = await apiClient.post('/login', { username: email, password });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  getToken: async (email, password) => {
    try {
      const response = await apiClient.post('/token', 
        new URLSearchParams({
          'username': email,
          'password': password
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      );
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

// Email services
export const emailService = {
  getEmails: async (limit = 20, offset = 0, category = null) => {
    try {
      const params = { limit, offset };
      if (category) params.category = category;
      
      const response = await apiClient.get('/emails/', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  getEmailById: async (messageId) => {
    try {
      const response = await apiClient.get(`/emails/${messageId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  analyzeEmail: async (content, subject, sender) => {
    try {
      const response = await apiClient.post('/emails/analyze', {
        content,
        subject,
        sender
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  processBatch: async (batchSize = 50) => {
    try {
      const response = await apiClient.post('/emails/process-batch', null, {
        params: { batch_size: batchSize }
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  getStats: async () => {
    try {
      const response = await apiClient.get('/emails/stats');
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  getSettings: async () => {
    try {
      const response = await apiClient.get('/emails/settings');
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  updateSettings: async (settings) => {
    try {
      const response = await apiClient.put('/emails/settings', settings);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

// Dashboard services
export const dashboardService = {
  getStats: async (period = 'day') => {
    try {
      const response = await apiClient.get('/dashboard/stats', { 
        params: { period } 
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  getUserActivity: async () => {
    try {
      const response = await apiClient.get('/dashboard/user-activity');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  getEmailAccountStats: async () => {
    try {
      const response = await apiClient.get('/dashboard/email-accounts');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  getDashboardSummary: async (period = 'day') => {
    try {
      const response = await apiClient.get('/dashboard/summary', {
        params: { period }
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default {
  auth: authService,
  emails: emailService,
  dashboard: dashboardService
};