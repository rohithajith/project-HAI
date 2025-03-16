import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Tabs, 
  Tab, 
  Paper,
  Button,
  CircularProgress
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import BookingList from '../components/bookings/BookingList';
import { useBookings } from '../contexts/BookingContext';

const Bookings = () => {
  const [tabValue, setTabValue] = useState(0);
  const [refreshing, setRefreshing] = useState(false);
  
  const { 
    allBookings, 
    upcomingBookings, 
    currentBookings, 
    pastBookings,
    loading, 
    error,
    fetchAllCategories
  } = useBookings();

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await fetchAllCategories();
    } catch (error) {
      console.error('Error refreshing bookings:', error);
    } finally {
      setRefreshing(false);
    }
  };

  // Determine which bookings to display based on selected tab
  const getBookingsForTab = () => {
    switch (tabValue) {
      case 0:
        return allBookings;
      case 1:
        return currentBookings;
      case 2:
        return upcomingBookings;
      case 3:
        return pastBookings;
      default:
        return allBookings;
    }
  };

  // Get title for the current tab
  const getTabTitle = () => {
    switch (tabValue) {
      case 0:
        return 'All Bookings';
      case 1:
        return 'Current Bookings';
      case 2:
        return 'Upcoming Bookings';
      case 3:
        return 'Past Bookings';
      default:
        return 'Bookings';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Bookings
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
      
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab label="All" />
          <Tab label="Current" />
          <Tab label="Upcoming" />
          <Tab label="Past" />
        </Tabs>
      </Paper>
      
      <BookingList 
        bookings={getBookingsForTab()} 
        title={getTabTitle()} 
        loading={loading} 
        error={error} 
      />
    </Box>
  );
};

export default Bookings;