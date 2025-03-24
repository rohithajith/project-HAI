import React, { useState } from 'react';
import { Box, Button, Typography, Slider } from '@mui/material';

const RoomControl = () => {
  const [temperature, setTemperature] = useState(22);

  const handleTemperatureChange = (event, newValue) => {
    setTemperature(newValue);
  };

  return (
    <Box sx={{ width: '100%', maxWidth: 400, margin: '0 auto', textAlign: 'center' }}>
      <Typography variant="h5" gutterBottom>
        Room Temperature Control
      </Typography>
      <Typography variant="body1" gutterBottom>
        Current Temperature: {temperature}°C
      </Typography>
      <Slider
        value={temperature}
        onChange={handleTemperatureChange}
        valueLabelDisplay="auto"
        step={1}
        marks
        min={16}
        max={30}
      />
      <Button variant="contained" color="primary" sx={{ mt: 2 }}>
        Set Temperature
      </Button>
    </Box>
  );
};

export default RoomControl;