import React from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Button,
  CircularProgress
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import AlertButton from '../components/alerts/AlertButton';
import AlertList from '../components/alerts/AlertList';
import { useAlerts } from '../contexts/AlertContext';

const Alerts = () => {
  const { 
    fetchAlerts, 
    resetAlertCount, 
    loading,
    alertCount
  } = useAlerts();
  
  const [refreshing, setRefreshing] = React.useState(false);
  const [resetting, setResetting] = React.useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await fetchAlerts();
    } catch (error) {
      console.error('Error refreshing alerts:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const handleResetCounter = async () => {
    setResetting(true);
    try {
      await resetAlertCount();
    } catch (error) {
      console.error('Error resetting alert counter:', error);
    } finally {
      setResetting(false);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Alerts
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={refreshing ? <CircularProgress size={20} /> : <RefreshIcon />}
            onClick={handleRefresh}
            disabled={refreshing || loading}
          >
            Refresh
          </Button>
          
          <Button
            variant="outlined"
            color="secondary"
            startIcon={resetting ? <CircularProgress size={20} /> : <RestartAltIcon />}
            onClick={handleResetCounter}
            disabled={resetting || alertCount === 0}
          >
            Reset Counter
          </Button>
        </Box>
      </Box>
      
      <Grid container spacing={3}>
        {/* Alert Button */}
        <Grid item xs={12} md={4}>
          <Box sx={{ height: '100%' }}>
            <AlertButton />
          </Box>
        </Grid>
        
        {/* Alert List */}
        <Grid item xs={12} md={8}>
          <AlertList />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Alerts;