import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
  CircularProgress,
  Chip,
  TextField,
  InputAdornment,
  IconButton
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';

const BookingList = ({ bookings, title, loading, error }) => {
  const [searchTerm, setSearchTerm] = useState('');
  
  // Filter bookings based on search term
  const filteredBookings = bookings.filter(booking => {
    const searchLower = searchTerm.toLowerCase();
    return (
      (booking.guest_name && booking.guest_name.toLowerCase().includes(searchLower)) ||
      (booking.room_number && booking.room_number.toLowerCase().includes(searchLower))
    );
  });

  // Handle search input change
  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  // Clear search
  const handleClearSearch = () => {
    setSearchTerm('');
  };

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  // Get status chip based on booking dates
  const getStatusChip = (booking) => {
    const now = new Date();
    const checkIn = new Date(booking.check_in);
    const checkOut = new Date(booking.check_out);
    
    if (checkIn > now) {
      return <Chip label="Upcoming" color="primary" size="small" />;
    } else if (checkIn <= now && checkOut >= now) {
      return <Chip label="Current" color="success" size="small" />;
    } else {
      return <Chip label="Past" color="default" size="small" />;
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

  return (
    <Paper elevation={2} sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" component="div">
          {title} ({filteredBookings.length})
        </Typography>
        
        <TextField
          variant="outlined"
          size="small"
          placeholder="Search by guest or room"
          value={searchTerm}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
            endAdornment: searchTerm && (
              <InputAdornment position="end">
                <IconButton
                  size="small"
                  aria-label="clear search"
                  onClick={handleClearSearch}
                >
                  <ClearIcon />
                </IconButton>
              </InputAdornment>
            )
          }}
        />
      </Box>
      
      {filteredBookings.length === 0 ? (
        <Typography variant="body1" align="center" sx={{ p: 3 }}>
          No bookings found.
        </Typography>
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table sx={{ minWidth: 650 }} aria-label="bookings table">
            <TableHead>
              <TableRow>
                <TableCell>Guest Name</TableCell>
                <TableCell>Room</TableCell>
                <TableCell>Check-in</TableCell>
                <TableCell>Check-out</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredBookings.map((booking) => (
                <TableRow key={booking.id} hover>
                  <TableCell component="th" scope="row">
                    {booking.guest_name || 'N/A'}
                  </TableCell>
                  <TableCell>{booking.room_number || 'N/A'}</TableCell>
                  <TableCell>{formatDate(booking.check_in)}</TableCell>
                  <TableCell>{formatDate(booking.check_out)}</TableCell>
                  <TableCell>{getStatusChip(booking)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Paper>
  );
};

export default BookingList;