import React from 'react';
import { Grid, Typography, Paper, Box } from '@mui/material';
import AlertButton from '../components/alerts/AlertButton';
import BookingList from '../components/bookings/BookingList';
import LaundryAlertForm from '../components/notifications/LaundryAlertForm';
import { useBookings } from '../contexts/BookingContext';

const Dashboard = () => {
  const { 
    currentBookings, 
    upcomingBookings, 
    loading: bookingsLoading, 
    error: bookingsError 
  } = useBookings();

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Alert Button */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3, height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <AlertButton />
          </Paper>
        </Grid>
        
        {/* Laundry Alert Form */}
        <Grid item xs={12} md={6}>
          <LaundryAlertForm />
        </Grid>
        
        {/* Current Bookings */}
        <Grid item xs={12} md={6}>
          <BookingList 
            bookings={currentBookings} 
            title="Current Bookings" 
            loading={bookingsLoading} 
            error={bookingsError} 
          />
        </Grid>
        
        {/* Upcoming Bookings */}
        <Grid item xs={12} md={6}>
          <BookingList 
            bookings={upcomingBookings} 
            title="Upcoming Bookings" 
            loading={bookingsLoading} 
            error={bookingsError} 
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;