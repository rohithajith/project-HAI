import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const RoomControl = () => {
  const navigate = useNavigate();

  const handleThermostat = () => {
    alert('Thermostat control placeholder');
  };

  const handleSOS = () => {
    // Navigate to alerts or trigger SOS action
    // Assuming '/alerts' is the correct path based on LandingPage.js
    navigate('/alerts');
    alert('SOS Alert Triggered!'); // Placeholder feedback
  };

  const handleCall = () => {
    alert('Call reception placeholder');
  };

  return (
    <Box sx={{ p: 2, border: '1px dashed grey' }}>
      <Typography variant="h6" gutterBottom>Room Controls</Typography>
      {/* Add specific room controls here based on sketch/requirements */}
      <Button variant="outlined" onClick={handleThermostat} sx={{ mr: 1 }}>Thermostat</Button>
      <Button variant="contained" color="error" onClick={handleSOS} sx={{ mr: 1 }}>SOS</Button>
      <Button variant="outlined" onClick={handleCall}>Call Reception</Button>
      {/* Placeholder for other controls */}
    </Box>
  );
};

export default RoomControl;