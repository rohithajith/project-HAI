import React from 'react';
import {
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Typography,
  Paper,
  Divider,
  Chip,
  Box,
  CircularProgress,
  Badge
} from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import DoneIcon from '@mui/icons-material/Done';
import LocalLaundryServiceIcon from '@mui/icons-material/LocalLaundryService';
import { useNotifications } from '../../contexts/NotificationContext';

const NotificationList = ({ roomNumber }) => {
  const { 
    notifications, 
    roomNotifications, 
    loading, 
    error, 
    fetchNotificationsByRoom,
    markNotificationAsRead 
  } = useNotifications();

  // Determine which notifications to display
  const displayNotifications = roomNumber 
    ? (roomNotifications[roomNumber] || []) 
    : notifications;

  // Handle marking a notification as read
  const handleMarkAsRead = async (id) => {
    try {
      await markNotificationAsRead(id);
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  // Get icon based on notification content
  const getNotificationIcon = (notification) => {
    if (notification.message && notification.message.toLowerCase().includes('laundry')) {
      return <LocalLaundryServiceIcon color="primary" />;
    }
    return <NotificationsIcon color="primary" />;
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Typography color="error" align="center">
        Error: {error}
      </Typography>
    );
  }

  if (displayNotifications.length === 0) {
    return (
      <Typography variant="body1" align="center" sx={{ p: 3 }}>
        No notifications found.
      </Typography>
    );
  }

  return (
    <Paper elevation={2}>
      <List sx={{ width: '100%' }}>
        <ListItem>
          <ListItemText
            primary={
              <Typography variant="h6">
                {roomNumber ? `Notifications for Room ${roomNumber}` : 'All Notifications'}
              </Typography>
            }
            secondary={`${displayNotifications.length} notifications total`}
          />
        </ListItem>
        <Divider />
        
        {displayNotifications.map((notification, index) => (
          <React.Fragment key={notification.id}>
            <ListItem>
              <ListItemIcon>
                {notification.is_read ? (
                  getNotificationIcon(notification)
                ) : (
                  <Badge color="error" variant="dot">
                    {getNotificationIcon(notification)}
                  </Badge>
                )}
              </ListItemIcon>
              
              <ListItemText
                primary={
                  <Typography 
                    variant="subtitle1"
                    sx={{ fontWeight: notification.is_read ? 'normal' : 'bold' }}
                  >
                    {notification.message}
                  </Typography>
                }
                secondary={
                  <Box sx={{ mt: 1 }}>
                    {notification.room_number && (
                      <Chip 
                        label={`Room ${notification.room_number}`} 
                        size="small" 
                        sx={{ mr: 1 }}
                      />
                    )}
                    
                    <Typography variant="caption" color="text.secondary">
                      {new Date(notification.created_at).toLocaleString()}
                    </Typography>
                    
                    {notification.is_read && (
                      <Chip 
                        icon={<DoneIcon />} 
                        label="Read" 
                        color="success" 
                        size="small"
                        sx={{ ml: 1 }}
                      />
                    )}
                  </Box>
                }
              />
              
              {!notification.is_read && (
                <ListItemSecondaryAction>
                  <IconButton 
                    edge="end" 
                    aria-label="mark as read" 
                    onClick={() => handleMarkAsRead(notification.id)}
                  >
                    <DoneIcon color="action" />
                  </IconButton>
                </ListItemSecondaryAction>
              )}
            </ListItem>
            
            {index < displayNotifications.length - 1 && <Divider variant="inset" component="li" />}
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
};

export default NotificationList;