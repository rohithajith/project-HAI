import React, { useState, useEffect } from 'react';
import { Box, Typography, CircularProgress, Paper, Tabs, Tab, List, ListItem, ListItemText } from '@mui/material';
import axios from 'axios'; // To fetch data from backend API

// Helper function to format date as YYYY-MM-DD
const formatDate = (date) => {
  const d = new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const AdminBookings = () => {
  const [bookings, setBookings] = useState({ previous: [], today: [], tomorrow: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(1); // 0: Previous, 1: Today, 2: Tomorrow

  useEffect(() => {
    const fetchBookings = async () => {
      setLoading(true);
      setError(null);
      try {
        // Fetch data from the actual API endpoint
        const response = await axios.get('/api/admin/bookings/filtered');
        setBookings(response.data); // Use data from the API response

      } catch (err) {
        console.error("Error fetching bookings:", err);
        setError("Failed to load bookings. Please check the backend connection.");
      } finally {
        setLoading(false);
      }
    };

    fetchBookings();
  }, []);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const renderBookingList = (bookingList) => {
    if (!bookingList || bookingList.length === 0) {
      return <Typography sx={{ p: 2 }}>No bookings for this period.</Typography>;
    }
    return (
      <List dense>
        {bookingList.map((booking) => (
          <ListItem key={booking.id}>
            <ListItemText
              primary={`Room ${booking.roomNumber} - ${booking.guestName}`}
              secondary={`Check-in: ${booking.checkIn}, Check-out: ${booking.checkOut}`}
            />
          </ListItem>
        ))}
      </List>
    );
  };

  return (
    <Paper elevation={2} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>Bookings Overview</Typography>
      {loading && <CircularProgress />}
      {error && <Typography color="error">{error}</Typography>}
      {!loading && !error && (
        <Box sx={{ width: '100%' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={activeTab} onChange={handleTabChange} aria-label="Booking date filter tabs">
              <Tab label="Previous Day" />
              <Tab label="Today" />
              <Tab label="Tomorrow" />
            </Tabs>
          </Box>
          <Box hidden={activeTab !== 0}>
            {renderBookingList(bookings.previous)}
          </Box>
           <Box hidden={activeTab !== 1}>
            {renderBookingList(bookings.today)}
          </Box>
           <Box hidden={activeTab !== 2}>
            {renderBookingList(bookings.tomorrow)}
          </Box>
        </Box>
      )}
    </Paper>
  );
};

export default AdminBookings;