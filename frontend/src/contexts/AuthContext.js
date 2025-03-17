import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

// Create context
const AuthContext = createContext();

// API base URL
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedUser = localStorage.getItem('user');
        const storedToken = localStorage.getItem('accessToken');
        
        if (storedUser && storedToken) {
          // Set default auth header
          axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
          
          // Fetch current user data to validate token
          await getCurrentUser();
        } else {
          setLoading(false);
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        logout();
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // Register a new user
  const register = async (userData) => {
    try {
      setError(null);
      setLoading(true);
      
      const response = await axios.post(`${API_URL}/auth/register`, userData);
      
      const { user, accessToken, refreshToken } = response.data.data;
      
      // Store tokens and user data
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      localStorage.setItem('user', JSON.stringify(user));
      
      // Set default auth header
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
      
      setCurrentUser(user);
      setLoading(false);
      
      return user;
    } catch (error) {
      setLoading(false);
      const message = error.response?.data?.message || 'Registration failed';
      setError(message);
      throw new Error(message);
    }
  };

  // Login user
  const login = async (email, password) => {
    try {
      setError(null);
      setLoading(true);
      
      const response = await axios.post(`${API_URL}/auth/login`, { email, password });
      
      const { user, accessToken, refreshToken } = response.data.data;
      
      // Store tokens and user data
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      localStorage.setItem('user', JSON.stringify(user));
      
      // Set default auth header
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
      
      setCurrentUser(user);
      setLoading(false);
      
      return user;
    } catch (error) {
      setLoading(false);
      const message = error.response?.data?.message || 'Login failed';
      setError(message);
      throw new Error(message);
    }
  };

  // Logout user
  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      
      if (refreshToken) {
        // Call logout API to invalidate the token
        await axios.post(`${API_URL}/auth/logout`, { refreshToken });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local storage and state
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
      
      // Remove auth header
      delete axios.defaults.headers.common['Authorization'];
      
      setCurrentUser(null);
    }
  };

  // Get current user data
  const getCurrentUser = async () => {
    try {
      setLoading(true);
      
      const response = await axios.get(`${API_URL}/auth/me`);
      
      const userData = response.data.data.user;
      
      // Update stored user data
      localStorage.setItem('user', JSON.stringify(userData));
      
      setCurrentUser(userData);
      setLoading(false);
      
      return userData;
    } catch (error) {
      console.error('Get current user error:', error);
      
      // If token is invalid, logout
      if (error.response?.status === 401) {
        logout();
      }
      
      setLoading(false);
      throw error;
    }
  };

  // Refresh token
  const refreshToken = async () => {
    try {
      const storedRefreshToken = localStorage.getItem('refreshToken');
      
      if (!storedRefreshToken) {
        throw new Error('No refresh token available');
      }
      
      const response = await axios.post(`${API_URL}/auth/refresh-token`, {
        refreshToken: storedRefreshToken
      });
      
      const { accessToken, refreshToken } = response.data.data;
      
      // Store new tokens
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      
      // Set default auth header
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
      
      return true;
    } catch (error) {
      console.error('Token refresh error:', error);
      logout();
      return false;
    }
  };

  // Check if user has a specific role
  const hasRole = (role) => {
    if (!currentUser || !currentUser.roles) return false;
    return currentUser.roles.includes(role);
  };

  // Check if user has a specific permission
  const hasPermission = (resource, action) => {
    if (!currentUser || !currentUser.permissions) return false;
    return currentUser.permissions.includes(`${resource}:${action}`);
  };

  // Request password reset
  const requestPasswordReset = async (email) => {
    try {
      setError(null);
      setLoading(true);
      
      const response = await axios.post(`${API_URL}/auth/password/reset-request`, { email });
      
      setLoading(false);
      return response.data;
    } catch (error) {
      setLoading(false);
      const message = error.response?.data?.message || 'Password reset request failed';
      setError(message);
      throw new Error(message);
    }
  };

  // Reset password with token
  const resetPassword = async (token, newPassword) => {
    try {
      setError(null);
      setLoading(true);
      
      const response = await axios.post(`${API_URL}/auth/password/reset`, {
        token,
        newPassword
      });
      
      setLoading(false);
      return response.data;
    } catch (error) {
      setLoading(false);
      const message = error.response?.data?.message || 'Password reset failed';
      setError(message);
      throw new Error(message);
    }
  };

  // Change password
  const changePassword = async (currentPassword, newPassword) => {
    try {
      setError(null);
      setLoading(true);
      
      const response = await axios.post(`${API_URL}/auth/password/change`, {
        currentPassword,
        newPassword
      });
      
      setLoading(false);
      return response.data;
    } catch (error) {
      setLoading(false);
      const message = error.response?.data?.message || 'Password change failed';
      setError(message);
      throw new Error(message);
    }
  };

  // Setup axios interceptor for token refresh
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        // If error is 401 and not a retry
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            // Try to refresh the token
            const refreshed = await refreshToken();
            
            if (refreshed) {
              // Retry the original request
              return axios(originalRequest);
            }
          } catch (refreshError) {
            console.error('Token refresh interceptor error:', refreshError);
          }
        }
        
        return Promise.reject(error);
      }
    );
    
    // Clean up interceptor on unmount
    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, []);

  const value = {
    currentUser,
    loading,
    error,
    register,
    login,
    logout,
    getCurrentUser,
    hasRole,
    hasPermission,
    requestPasswordReset,
    resetPassword,
    changePassword
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;