import React from 'react';
import { Box, Container, CssBaseline, Typography, AppBar, Toolbar, Button } from '@mui/material';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import ChatIcon from '@mui/icons-material/Chat';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';

/**
 * GuestLayout component - Provides a consistent layout for guest pages
 * Includes a simplified header with chatbot access and logout functionality
 */
const GuestLayout = () => {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <CssBaseline />
      
      {/* Guest Header */}
      <AppBar position="static" color="primary" elevation={2}>
        <Toolbar>
          <ChatIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Hotel Guest Portal
          </Typography>
          
          {currentUser && (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="body1" sx={{ mr: 2 }}>
                Welcome, {currentUser.firstName || 'Guest'}
              </Typography>
              <Button 
                color="inherit" 
                startIcon={<ExitToAppIcon />}
                onClick={handleLogout}
              >
                Logout
              </Button>
            </Box>
          )}
        </Toolbar>
      </AppBar>
      
      {/* Main Content */}
      <Container component="main" sx={{ flexGrow: 1, py: 3 }}>
        <Outlet />
      </Container>
      
      {/* Footer */}
      <Box
        component="footer"
        sx={{
          py: 2,
          mt: 'auto',
          backgroundColor: (theme) =>
            theme.palette.mode === 'light'
              ? theme.palette.grey[200]
              : theme.palette.grey[800],
          textAlign: 'center',
        }}
      >
        <Container maxWidth="sm">
          <Typography variant="body2" color="text.secondary">
            © {new Date().getFullYear()} Luxury Hotel Experience
          </Typography>
        </Container>
      </Box>
    </Box>
  );
};

export default GuestLayout;