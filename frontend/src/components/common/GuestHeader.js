import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box, IconButton } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import HotelIcon from '@mui/icons-material/Hotel';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import ChatIcon from '@mui/icons-material/Chat';
import { useAuth } from '../../contexts/AuthContext';

const GuestHeader = () => {
  const { currentUser, logout } = useAuth();
  
  const handleLogout = async () => {
    try {
      await logout();
      // Redirect will be handled by the auth context
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <HotelIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Luxury Hotel Experience
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            color="inherit"
            component={RouterLink}
            to="/guest"
          >
            Room Controls
          </Button>
          
          <Button
            color="inherit"
            component={RouterLink}
            to="/guest#chat"
            startIcon={<ChatIcon />}
          >
            AI Assistant
          </Button>
          
          {currentUser ? (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <IconButton
                color="inherit"
                edge="end"
                aria-label="account"
                sx={{ ml: 2 }}
              >
                <AccountCircleIcon />
              </IconButton>
              <Typography variant="body2" sx={{ ml: 1 }}>
                {currentUser.name || currentUser.email}
              </Typography>
              <Button 
                color="inherit" 
                onClick={handleLogout}
                sx={{ ml: 2 }}
              >
                Logout
              </Button>
            </Box>
          ) : (
            <Button 
              color="inherit" 
              component={RouterLink} 
              to="/login"
            >
              Login
            </Button>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default GuestHeader;