import React, { useState } from 'react';
import {
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
  Snackbar,
  CircularProgress
} from '@mui/material';
import LocalLaundryServiceIcon from '@mui/icons-material/LocalLaundryService';
import { useNotifications } from '../../contexts/NotificationContext';

const LaundryAlertForm = () => {
  const { sendLaundryAlert } = useNotifications();
  const [roomNumber, setRoomNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!roomNumber.trim()) {
      setError('Room number is required');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      await sendLaundryAlert(roomNumber);
      setSuccess(true);
      setRoomNumber('');
    } catch (err) {
      setError(err.message || 'Failed to send laundry alert');
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSuccess(false);
  };

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Send Laundry Alert
      </Typography>
      
      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
        <TextField
          fullWidth
          label="Room Number"
          variant="outlined"
          value={roomNumber}
          onChange={(e) => setRoomNumber(e.target.value)}
          placeholder="Enter room number"
          margin="normal"
          error={!!error}
          helperText={error}
          disabled={loading}
          InputProps={{
            startAdornment: (
              <Box sx={{ mr: 1, color: 'text.secondary' }}>
                <LocalLaundryServiceIcon />
              </Box>
            ),
          }}
        />
        
        <Button
          type="submit"
          variant="contained"
          color="primary"
          fullWidth
          sx={{ mt: 2 }}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Send Laundry Alert'}
        </Button>
      </Box>
      
      <Snackbar
        open={success}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
          Laundry alert sent successfully to Room {roomNumber}!
        </Alert>
      </Snackbar>
    </Paper>
  );
};

export default LaundryAlertForm;