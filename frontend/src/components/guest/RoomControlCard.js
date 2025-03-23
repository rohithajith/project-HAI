import React from 'react';
import { Paper, Box, Typography, Divider } from '@mui/material';
import TemperatureControl from './RoomControls/TemperatureControl';
import LightingControl from './RoomControls/LightingControl';
import PresetControls from './RoomControls/PresetControls';

const RoomControlCard = () => {
  return (
    <Paper 
      elevation={3} 
      sx={{ 
        p: 3, 
        height: '100%',
        borderRadius: 2,
        boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
        overflow: 'auto'
      }}
    >
      <Typography 
        variant="h5" 
        component="h2" 
        sx={{ 
          mb: 3, 
          fontWeight: 'bold',
          color: 'primary.main'
        }}
      >
        Room Controls
      </Typography>
      
      <TemperatureControl />
      
      <Divider sx={{ my: 2 }} />
      
      <LightingControl />
      
      <Divider sx={{ my: 2 }} />
      
      <PresetControls />
    </Paper>
  );
};

export default RoomControlCard;