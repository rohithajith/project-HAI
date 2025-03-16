import React from 'react';
import { AppBar, Toolbar, Typography, Button, Badge, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import NotificationsIcon from '@mui/icons-material/Notifications';
import HotelIcon from '@mui/icons-material/Hotel';
import { useAlerts } from '../../contexts/AlertContext';
import { useNotifications } from '../../contexts/NotificationContext';

const Header = () => {
  const { alertCount } = useAlerts();
  const { notifications } = useNotifications();
  
  // Count unread notifications
  const unreadCount = notifications.filter(notification => !notification.is_read).length;

  return (
    <AppBar position="static">
      <Toolbar>
        <HotelIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Hotel Management System
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button color="inherit" component={RouterLink} to="/">
            Dashboard
          </Button>
          
          <Button color="inherit" component={RouterLink} to="/bookings">
            Bookings
          </Button>
          
          <Button 
            color="inherit" 
            component={RouterLink} 
            to="/alerts"
            startIcon={
              <Badge badgeContent={alertCount} color="error">
                <NotificationsIcon />
              </Badge>
            }
          >
            Alerts
          </Button>
          
          <Button 
            color="inherit" 
            component={RouterLink} 
            to="/notifications"
            startIcon={
              <Badge badgeContent={unreadCount} color="error">
                <NotificationsIcon />
              </Badge>
            }
          >
            Notifications
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;