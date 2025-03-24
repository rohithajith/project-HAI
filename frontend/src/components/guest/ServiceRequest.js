import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  MenuItem, 
  FormControl, 
  InputLabel, 
  Select, 
  Paper, 
  Grid,
  Snackbar,
  Alert,
  CircularProgress
} from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

/**
 * ServiceRequest component - Allows guests to submit service requests
 * These requests will be visible in the admin dashboard
 */
const ServiceRequest = () => {
  const { currentUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  
  // Form state
  const [formData, setFormData] = useState({
    serviceType: '',
    description: '',
    urgency: 'normal',
    preferredTime: ''
  });
  
  // Service types
  const serviceTypes = [
    { value: 'room_service', label: 'Room Service' },
    { value: 'housekeeping', label: 'Housekeeping' },
    { value: 'maintenance', label: 'Maintenance' },
    { value: 'concierge', label: 'Concierge Assistance' },
    { value: 'spa', label: 'Spa & Wellness' },
    { value: 'transportation', label: 'Transportation' }
  ];
  
  // Urgency levels
  const urgencyLevels = [
    { value: 'low', label: 'Low - When Convenient' },
    { value: 'normal', label: 'Normal - Today' },
    { value: 'high', label: 'High - As Soon As Possible' },
    { value: 'urgent', label: 'Urgent - Immediate Attention Required' }
  ];
  
  // Handle form input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      // Prepare request data
      const requestData = {
        ...formData,
        userId: currentUser?.id,
        roomNumber: currentUser?.profile?.room_number || '301',
        guestName: `${currentUser?.firstName || 'Guest'} ${currentUser?.lastName || ''}`,
        status: 'pending',
        createdAt: new Date().toISOString()
      };
      
      // Send request to backend
      await axios.post('http://localhost:5000/api/notifications', requestData);
      
      // Show success message
      setSuccess(true);
      
      // Reset form
      setFormData({
        serviceType: '',
        description: '',
        urgency: 'normal',
        preferredTime: ''
      });
    } catch (err) {
      console.error('Error submitting service request:', err);
      setError('Failed to submit service request. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  // Handle snackbar close
  const handleSnackbarClose = () => {
    setSuccess(false);
  };
  
  return (
    <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
      <Typography variant="h5" gutterBottom>
        Request Service
      </Typography>
      
      <Typography variant="body2" color="text.secondary" paragraph>
        Submit your service request and our staff will attend to it promptly.
      </Typography>
      
      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
        <Grid container spacing={3}>
          {/* Service Type */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth required>
              <InputLabel id="service-type-label">Service Type</InputLabel>
              <Select
                labelId="service-type-label"
                id="serviceType"
                name="serviceType"
                value={formData.serviceType}
                onChange={handleChange}
                label="Service Type"
              >
                {serviceTypes.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          {/* Urgency */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth required>
              <InputLabel id="urgency-label">Urgency</InputLabel>
              <Select
                labelId="urgency-label"
                id="urgency"
                name="urgency"
                value={formData.urgency}
                onChange={handleChange}
                label="Urgency"
              >
                {urgencyLevels.map((level) => (
                  <MenuItem key={level.value} value={level.value}>
                    {level.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          {/* Preferred Time */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              id="preferredTime"
              name="preferredTime"
              label="Preferred Time (Optional)"
              value={formData.preferredTime}
              onChange={handleChange}
              placeholder="e.g., After 3 PM"
            />
          </Grid>
          
          {/* Room Number (Auto-filled) */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              id="roomNumber"
              label="Room Number"
              value={currentUser?.profile?.room_number || '301'}
              InputProps={{
                readOnly: true,
              }}
            />
          </Grid>
          
          {/* Description */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              id="description"
              name="description"
              label="Description"
              value={formData.description}
              onChange={handleChange}
              multiline
              rows={4}
              required
              placeholder="Please provide details about your request..."
            />
          </Grid>
          
          {/* Submit Button */}
          <Grid item xs={12}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              size="large"
              disabled={loading}
              sx={{ mt: 2 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Submit Request'}
            </Button>
          </Grid>
        </Grid>
      </Box>
      
      {/* Success Message */}
      <Snackbar
        open={success}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleSnackbarClose} severity="success" sx={{ width: '100%' }}>
          Your service request has been submitted successfully!
        </Alert>
      </Snackbar>
      
      {/* Error Message */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Paper>
  );
};

export default ServiceRequest;