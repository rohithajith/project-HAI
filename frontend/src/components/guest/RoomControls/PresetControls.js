import React from 'react';
import { Button, Typography, Box, Grid, Paper } from '@mui/material';
import { useRoomControl } from '../../../contexts/RoomControlContext';

const PresetControls = () => {
  const { presets, applyPreset, activePreset, saveCustomPreset } = useRoomControl();
  
  // Convert presets object to array for mapping
  const presetArray = Object.entries(presets).map(([key, preset]) => ({
    id: key,
    ...preset
  }));
  
  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>Preset Controls</Typography>
      
      <Grid container spacing={2}>
        {presetArray.map((preset) => (
          <Grid item xs={6} key={preset.id}>
            <Button
              fullWidth
              variant={activePreset === preset.id ? "contained" : "outlined"}
              onClick={() => preset.id === 'custom' ? saveCustomPreset() : applyPreset(preset.id)}
              sx={{
                height: '80px',
                transition: 'all 0.3s ease',
                borderWidth: activePreset === preset.id ? 2 : 1,
                boxShadow: activePreset === preset.id ? 3 : 0,
                display: 'flex',
                flexDirection: 'column',
                animation: activePreset === preset.id ? 'pulse 2s infinite' : 'none',
                '@keyframes pulse': {
                  '0%': {
                    boxShadow: activePreset === preset.id ? '0 0 0 0 rgba(25, 118, 210, 0.4)' : 'none',
                  },
                  '70%': {
                    boxShadow: activePreset === preset.id ? '0 0 0 10px rgba(25, 118, 210, 0)' : 'none',
                  },
                  '100%': {
                    boxShadow: activePreset === preset.id ? '0 0 0 0 rgba(25, 118, 210, 0)' : 'none',
                  },
                },
              }}
            >
              <Typography variant="h5" sx={{ mb: 1 }}>{preset.icon}</Typography>
              <Typography variant="body2">{preset.name}</Typography>
            </Button>
          </Grid>
        ))}
      </Grid>
      
      {activePreset && (
        <Paper 
          sx={{ 
            mt: 2, 
            p: 2, 
            bgcolor: 'rgba(0,0,0,0.02)',
            borderRadius: 2,
            border: '1px solid rgba(0,0,0,0.05)'
          }}
        >
          <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
            Active Preset: {presets[activePreset].name}
          </Typography>
          <Typography variant="body2">
            • Temperature: {presets[activePreset].temperature}°C
          </Typography>
          <Typography variant="body2">
            • Brightness: {presets[activePreset].brightness}%
          </Typography>
          <Typography variant="body2">
            • Color: {presets[activePreset].colorTemp < 50 ? 'Warm' : 'Cool'}
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default PresetControls;