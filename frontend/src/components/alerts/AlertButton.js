import React, { useState } from 'react';
import { Button, Badge, Typography, Box, CircularProgress } from '@mui/material';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import { useAlerts } from '../../contexts/AlertContext';

const AlertButton = () => {
  const { alertCount, triggerAlert, createAlert } = useAlerts();
  const [loading, setLoading] = useState(false);

  const handleAlertClick = async () => {
    setLoading(true);
    
    try {
      // Trigger WebSocket alert
      triggerAlert();
      
      // Also create an alert in the database
      await createAlert({
        type: 'general',
        message: 'Alert triggered from frontend'
      });
    } catch (error) {
      console.error('Error triggering alert:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
      <Button
        variant="contained"
        color="error"
        size="large"
        startIcon={<NotificationsActiveIcon />}
        onClick={handleAlertClick}
        disabled={loading}
        sx={{ 
          height: 60, 
          width: 200,
          fontSize: '1.2rem',
          fontWeight: 'bold'
        }}
      >
        {loading ? <CircularProgress size={24} color="inherit" /> : 'ALERT'}
      </Button>
      
      <Badge 
        badgeContent={alertCount} 
        color="error"
        max={999}
        sx={{ 
          '& .MuiBadge-badge': {
            fontSize: '1rem',
            height: '2rem',
            minWidth: '2rem',
            borderRadius: '1rem'
          }
        }}
      >
        <Typography variant="h6" component="div">
          Alert Count: {alertCount}
        </Typography>
      </Badge>
    </Box>
  );
};

export default AlertButton;