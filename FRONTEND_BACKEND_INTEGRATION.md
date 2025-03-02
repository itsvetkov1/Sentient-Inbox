# Sentient Inbox Frontend-Backend Integration Guide

This guide explains how to integrate the React frontend with the FastAPI backend for the Sentient Inbox application.

## Overview

The Sentient Inbox application consists of two main parts:
1. **Frontend**: React-based user interface
2. **Backend**: FastAPI-based RESTful API

## Prerequisites

Before proceeding, ensure you have:
- Both frontend and backend code cloned from the repository
- Node.js installed for the frontend
- Python 3.8+ installed for the backend
- Necessary environment variables configured

## Step 1: Start the Backend API Server

First, you'll need to start the FastAPI backend:

1. Navigate to the project root directory:
   ```bash
   cd /path/to/Sentient-Inbox
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the API server:
   ```bash
   python run_api.py
   ```

   This will start the API server on http://localhost:8000 by default.

5. Verify the API is running by accessing http://localhost:8000/docs in your browser

## Step 2: Configure Frontend to Connect to API

The frontend is already configured to connect to http://localhost:8000 through the `.env` file. If your API is running on a different URL or port, update the following file:

1. Open `/frontend/.env` and modify:
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```

   Change this to match your API server URL.

## Step 3: Implement API Service in Frontend

If you need to implement or modify API service calls:

1. Create an API service file (if not already existing):
   ```bash
   mkdir -p /frontend/src/services
   touch /frontend/src/services/api.js
   ```

2. Implement the API service functions:

```javascript
// /frontend/src/services/api.js
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

export default {
  auth: authService,
  emails: emailService
};
```

## Step 4: Using API Services in React Components

Here's how to use the API services in your React components:

### Login Example:

```javascript
import React, { useState } from 'react';
import { authService } from '../services/api';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const handleLogin = async (e) => {
    e.preventDefault();
    
    if (!email || !password) {
      setError('Please enter both email and password');
      return;
    }
    
    try {
      setLoading(true);
      setError('');
      
      // Call the API login endpoint
      const response = await authService.getToken(email, password);
      
      // Store the token
      localStorage.setItem('token', response.access_token);
      
      // Redirect to dashboard
      window.location.href = '/dashboard';
      
    } catch (err) {
      console.error('Login error:', err);
      setError('Invalid credentials. Please try again.');
      setLoading(false);
    }
  };
  
  // Rest of component...
};
```

### Fetching Emails Example:

```javascript
import React, { useState, useEffect } from 'react';
import { emailService } from '../services/api';

const EmailList = () => {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  useEffect(() => {
    const fetchEmails = async () => {
      try {
        setLoading(true);
        const response = await emailService.getEmails();
        setEmails(response.emails);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching emails:', err);
        setError('Failed to load emails. Please try again.');
        setLoading(false);
      }
    };
    
    fetchEmails();
  }, []);
  
  // Rest of component...
};
```

## Step 5: Start the Frontend Development Server

1. Navigate to the frontend directory:
   ```bash
   cd /path/to/Sentient-Inbox/frontend
   ```

2. Install dependencies (if not already done):
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Your browser should open automatically to http://localhost:3000

## Testing the Integration

1. Open the application in your browser
2. Navigate to the login page
3. Try logging in using the API authentication endpoints
4. Verify that API requests show up in your browser's Network tab
5. Check that responses are correctly handled in the UI

## Troubleshooting

### CORS Issues
If you experience CORS errors:

1. Verify your backend is configured to allow requests from your frontend origin
2. Check the CORS middleware configuration in `/api/main.py`
3. Make sure the allowed origins include your frontend URL (e.g., http://localhost:3000)

### Authentication Problems
If authentication isn't working:

1. Check browser console for errors
2. Verify the token is being properly stored in localStorage
3. Check that the Authorization header is correctly added to requests
4. Validate token expiration and refresh if needed

### API Connection Issues
If the frontend can't connect to the API:

1. Verify the API server is running
2. Check that the API URL in `.env` is correct
3. Test the API endpoints directly using a tool like Postman
4. Look for network errors in the browser console

## Next Steps

1. Implement additional API service functions as needed
2. Add authentication state management (using Context or Redux)
3. Implement protected routes for authenticated users
4. Add token refresh mechanism
5. Handle offline scenarios and error states