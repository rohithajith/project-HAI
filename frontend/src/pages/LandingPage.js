import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  Box, 
  Button, 
  Typography, 
  Grid, 
  Paper, 
  CircularProgress
} from '@mui/material';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import PersonIcon from '@mui/icons-material/Person';
import HotelIcon from '@mui/icons-material/Hotel';

/**
 * LandingPage component - Entry point that redirects users based on their role
 * If logged in, redirects to the appropriate dashboard
 * If not logged in, shows login options for admin or guest
 */
const LandingPage = () => {
  const navigate = useNavigate();
  const { currentUser, loading } = useAuth();

  // Redirect based on user role if logged in
  useEffect(() => {
    if (currentUser && !loading) {
      // Check if user has admin/staff role
      const isAdmin = currentUser.roles?.includes('admin') || 
                      currentUser.roles?.includes('staff') || 
                      currentUser.roles?.includes('manager');
      
      // Check if user has guest role
      const isGuest = currentUser.roles?.includes('guest');
      
      if (isAdmin) {
        navigate('/admin');
      } else if (isGuest) {
        navigate('/guest');
      }
    }
  }, [currentUser, loading, navigate]);

  // Handle login button clicks
  const handleLoginAs = (userType) => {
    navigate('/login', { state: { userType } });
  };

  // Show loading spinner while checking auth state
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  // If user is already logged in, this will be briefly shown before redirect
  if (currentUser) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Redirecting to your dashboard...
        </Typography>
      </Box>
    );
  }

  // Show login options for non-logged in users
  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box 
        sx={{ 
          bgcolor: 'primary.main', 
          color: 'white', 
          py: 2,
          px: 3,
          display: 'flex',
          alignItems: 'center'
        }}
      >
        <HotelIcon sx={{ mr: 2, fontSize: 32 }} />
        <Typography variant="h5" component="div">
          Hotel Management System
        </Typography>
      </Box>
      
      {/* Main Content */}
      <Box 
        sx={{ 
          flexGrow: 1, 
          display: 'flex', 
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          p: 3
        }}
      >
        <Typography variant="h3" component="h1" gutterBottom align="center">
          Welcome to Luxury Hotel
        </Typography>
        
        <Typography variant="h5" component="h2" gutterBottom align="center" sx={{ mb: 6, maxWidth: 600 }}>
          Please select how you would like to proceed
        </Typography>
        
        <Grid container spacing={4} justifyContent="center" sx={{ maxWidth: 900 }}>
          {/* Admin Login Option */}
          <Grid item xs={12} md={6}>
            <Paper 
              elevation={3} 
              sx={{ 
                p: 4, 
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                borderRadius: 2
              }}
            >
              <AdminPanelSettingsIcon sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                Staff & Admin
              </Typography>
              <Typography variant="body1" sx={{ mb: 4 }}>
                Access the hotel management system to manage bookings, handle guest requests, and monitor hotel operations.
              </Typography>
              <Button
                variant="contained"
                size="large"
                fullWidth
                onClick={() => handleLoginAs('admin')}
                sx={{ mt: 'auto' }}
              >
                Staff Login
              </Button>
            </Paper>
          </Grid>
          
          {/* Guest Login Option */}
          <Grid item xs={12} md={6}>
            <Paper 
              elevation={3} 
              sx={{ 
                p: 4, 
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                borderRadius: 2
              }}
            >
              <PersonIcon sx={{ fontSize: 80, color: 'secondary.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                Hotel Guest
              </Typography>
              <Typography variant="body1" sx={{ mb: 4 }}>
                Access guest services, chat with our AI concierge, request room service, and manage your stay experience.
              </Typography>
              <Button
                variant="contained"
                color="secondary"
                size="large"
                fullWidth
                onClick={() => handleLoginAs('guest')}
                sx={{ mt: 'auto' }}
              >
                Guest Login
              </Button>
            </Paper>
          </Grid>
        </Grid>
      </Box>
      
      {/* Footer */}
      <Box 
        component="footer" 
        sx={{ 
          py: 3, 
          bgcolor: 'primary.dark',
          color: 'white',
          textAlign: 'center'
        }}
      >
        <Typography variant="body2">
          © {new Date().getFullYear()} Luxury Hotel Management System
        </Typography>
      </Box>
    </Box>
  );
};

export default LandingPage;