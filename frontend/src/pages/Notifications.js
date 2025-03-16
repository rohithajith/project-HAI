import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Button,
  CircularProgress,
  TextField,
  InputAdornment,
  IconButton,
  Paper
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import LaundryAlertForm from '../components/notifications/LaundryAlertForm';
import NotificationList from '../components/notifications/NotificationList';
import { useNotifications } from '../contexts/NotificationContext';

const Notifications = () => {
  const { 
    fetchAllNotifications, 
    fetchNotificationsByRoom,
    loading
  } = useNotifications();
  
  const [refreshing, setRefreshing] = useState(false);
  const [roomNumber, setRoomNumber] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [searching, setSearching] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      if (roomNumber) {
        await fetchNotificationsByRoom(roomNumber);
      } else {
        await fetchAllNotifications();
      }
    } catch (error) {
      console.error('Error refreshing notifications:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const handleSearch = async () => {
    if (!searchInput.trim()) return;
    
    setSearching(true);
    try {
      setRoomNumber(searchInput);
      await fetchNotificationsByRoom(searchInput);
    } catch (error) {
      console.error('Error searching notifications:', error);
    } finally {
      setSearching(false);
    }
  };

  const handleClearSearch = async () => {
    setSearchInput('');
    setRoomNumber('');
    await fetchAllNotifications();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Notifications
        </Typography>
        
        <Button
          variant="outlined"
          startIcon={refreshing ? <CircularProgress size={20} /> : <RefreshIcon />}
          onClick={handleRefresh}
          disabled={refreshing || loading}
        >
          Refresh
        </Button>
      </Box>
      
      <Grid container spacing={3}>
        {/* Search and Laundry Alert Form */}
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Search by Room
            </Typography>
            
            <TextField
              fullWidth
              label="Room Number"
              variant="outlined"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter room number"
              margin="normal"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
                endAdornment: searchInput && (
                  <InputAdornment position="end">
                    <IconButton
                      size="small"
                      aria-label="clear search"
                      onClick={handleClearSearch}
                    >
                      <ClearIcon />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            
            <Button
              variant="contained"
              color="primary"
              fullWidth
              sx={{ mt: 1 }}
              onClick={handleSearch}
              disabled={searching || !searchInput.trim()}
            >
              {searching ? <CircularProgress size={24} /> : 'Search'}
            </Button>
          </Paper>
          
          <LaundryAlertForm />
        </Grid>
        
        {/* Notification List */}
        <Grid item xs={12} md={8}>
          <NotificationList roomNumber={roomNumber} />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Notifications;