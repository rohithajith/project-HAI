import React from 'react';
import { Slider, Typography, Box } from '@mui/material';
import { useRoomControl } from '../../../contexts/RoomControlContext';

const LightingControl = () => {
  const { brightness, setBrightness, colorTemp, setColorTemp } = useRoomControl();
  
  // Calculate preview background color based on brightness and color temp
  const getLightPreviewStyle = () => {
    // Convert brightness (0-100) to opacity (0.1-1)
    const opacity = 0.1 + (brightness / 100) * 0.9;
    
    // Convert colorTemp (0-100) from warm to cool
    // Warm: rgb(255, 244, 229) - Cool: rgb(240, 249, 255)
    const r = Math.round(255 - (colorTemp / 100) * 15);
    const g = Math.round(244 + (colorTemp / 100) * 5);
    const b = Math.round(229 + (colorTemp / 100) * 26);
    
    return {
      backgroundColor: `rgba(${r}, ${g}, ${b}, ${opacity})`,
      transition: 'background-color 0.5s ease',
      height: '80px',
      borderRadius: '8px',
      border: '1px solid rgba(0,0,0,0.1)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    };
  };
  
  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="h6" sx={{ mb: 1 }}>Lighting Control</Typography>
      
      <Typography variant="body2" sx={{ mb: 0.5, display: 'flex', justifyContent: 'space-between' }}>
        <span>Brightness:</span>
        <span>{brightness}%</span>
      </Typography>
      <Slider
        value={brightness}
        min={0}
        max={100}
        onChange={(_, value) => setBrightness(value)}
        sx={{ mb: 2 }}
        aria-label="Brightness"
      />
      
      <Typography variant="body2" sx={{ mb: 0.5 }}>
        Color Temperature
      </Typography>
      <Slider
        value={colorTemp}
        min={0}
        max={100}
        onChange={(_, value) => setColorTemp(value)}
        sx={{ mb: 2 }}
        aria-label="Color Temperature"
      />
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="body2" color="text.secondary">Warm</Typography>
        <Typography variant="body2" color="text.secondary">Cool</Typography>
      </Box>
      
      <Typography variant="body2" sx={{ mb: 0.5 }}>Preview:</Typography>
      <Box style={getLightPreviewStyle()}>
        <Box 
          sx={{ 
            width: '30px', 
            height: '30px', 
            borderRadius: '50%', 
            background: 'radial-gradient(circle, rgba(255,255,255,1) 0%, rgba(255,255,255,0) 70%)',
            opacity: brightness / 100,
            boxShadow: '0 0 10px 5px rgba(255,255,255,0.5)',
            transition: 'opacity 0.3s ease'
          }} 
        />
      </Box>
    </Box>
  );
};

export default LightingControl;