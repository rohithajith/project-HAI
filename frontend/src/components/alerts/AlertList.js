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
  CircularProgress
} from '@mui/material';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useAlerts } from '../../contexts/AlertContext';

const AlertList = () => {
  const { alerts, loading, error, resolveAlert } = useAlerts();

  const handleResolveAlert = async (id) => {
    try {
      await resolveAlert(id);
    } catch (error) {
      console.error('Error resolving alert:', error);
    }
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

  if (alerts.length === 0) {
    return (
      <Typography variant="body1" align="center" sx={{ p: 3 }}>
        No alerts found.
      </Typography>
    );
  }

  return (
    <Paper elevation={2}>
      <List sx={{ width: '100%' }}>
        <ListItem>
          <ListItemText
            primary={<Typography variant="h6">Alert History</Typography>}
            secondary={`${alerts.length} alerts total`}
          />
        </ListItem>
        <Divider />
        
        {alerts.map((alert, index) => (
          <React.Fragment key={alert.id}>
            <ListItem>
              <ListItemIcon>
                <NotificationsActiveIcon color="error" />
              </ListItemIcon>
              
              <ListItemText
                primary={
                  <Typography variant="subtitle1">
                    {alert.type.charAt(0).toUpperCase() + alert.type.slice(1)} Alert
                  </Typography>
                }
                secondary={
                  <Box sx={{ mt: 1 }}>
                    {alert.message && (
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {alert.message}
                      </Typography>
                    )}
                    
                    {alert.room_number && (
                      <Chip 
                        label={`Room ${alert.room_number}`} 
                        size="small" 
                        sx={{ mr: 1 }}
                      />
                    )}
                    
                    <Typography variant="caption" color="text.secondary">
                      {new Date(alert.created_at).toLocaleString()}
                    </Typography>
                  </Box>
                }
              />
              
              <ListItemSecondaryAction>
                {alert.is_resolved ? (
                  <Chip 
                    icon={<CheckCircleIcon />} 
                    label="Resolved" 
                    color="success" 
                    size="small" 
                  />
                ) : (
                  <IconButton 
                    edge="end" 
                    aria-label="resolve" 
                    onClick={() => handleResolveAlert(alert.id)}
                  >
                    <CheckCircleIcon color="action" />
                  </IconButton>
                )}
              </ListItemSecondaryAction>
            </ListItem>
            
            {index < alerts.length - 1 && <Divider variant="inset" component="li" />}
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
};

export default AlertList;