import React from 'react';
import { Slider, Typography, Box } from '@mui/material';
import { useRoomControl } from '../../../contexts/RoomControlContext';

const TemperatureControl = () => {
  const { temperature, setTemperature } = useRoomControl();
  
  // Get color based on temperature (blue for cold, red for hot)
  const getTemperatureColor = (temp) => {
    // Linear gradient from blue (18°C) to red (30°C)
    const ratio = (temp - 18) / (30 - 18);
    const r = Math.round(ratio * 255);
    const b = Math.round((1 - ratio) * 255);
    return `rgb(${r}, 0, ${b})`;
  };
  
  return (
    <Box sx={{ mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="h6">Temperature Control</Typography>
        <Typography 
          variant="h6" 
          sx={{ 
            color: getTemperatureColor(temperature),
            transition: 'color 0.3s ease',
            fontWeight: 'bold'
          }}
        >
          {temperature}°C
        </Typography>
      </Box>
      
      <Slider
        value={temperature}
        min={18}
        max={30}
        step={0.5}
        onChange={(_, value) => setTemperature(value)}
        sx={{
          '& .MuiSlider-thumb': {
            backgroundColor: getTemperatureColor(temperature),
            transition: 'background-color 0.3s ease'
          },
          '& .MuiSlider-track': {
            background: 'linear-gradient(to right, #2196f3, #f44336)',
          }
        }}
      />
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
        <Typography variant="body2" color="text.secondary">18°C (Cool)</Typography>
        <Typography variant="body2" color="text.secondary">30°C (Warm)</Typography>
      </Box>
    </Box>
  );
};

export default TemperatureControl;