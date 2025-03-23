import React from 'react';
import { Box } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { Navigate } from 'react-router-dom';
import GuestDashboard from '../components/guest/GuestDashboard';

/**
 * GuestPage component - Container page for the guest dashboard
 * Handles authentication and routing
 */
const GuestPage = () => {
  const { currentUser, loading } = useAuth();
  
  // Show loading state
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        Loading...
      </Box>
    );
  }
  
  // Redirect to login if not authenticated
  // Note: In a real hotel scenario, this might redirect to a check-in page or use a room code
  if (!currentUser) {
    return <Navigate to="/login" />;
  }
  
  // Check if user has guest role
  // This is a simplified check - in a real app, you'd check the user's roles from the auth context
  const isGuest = true; // For demo purposes, we're assuming all authenticated users can access guest features
  
  if (!isGuest) {
    return <Navigate to="/dashboard" />;
  }
  
  return <GuestDashboard />;
};

export default GuestPage;