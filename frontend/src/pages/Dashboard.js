import React, { useState, useEffect } from 'react';
import {
  Grid,
  Typography,
  Paper,
  Box,
  Divider,
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon, 
  Chip,
  Button,
  CircularProgress,
  Alert
} from '@mui/material';
import AlertButton from '../components/alerts/AlertButton';
import BookingList from '../components/bookings/BookingList';
import LaundryAlertForm from '../components/notifications/LaundryAlertForm';
import { useBookings } from '../contexts/BookingContext';
import axios from 'axios';
import RoomServiceIcon from '@mui/icons-material/RoomService';
import CleaningServicesIcon from '@mui/icons-material/CleaningServices';
import BuildIcon from '@mui/icons-material/Build';
import SupportAgentIcon from '@mui/icons-material/SupportAgent';
import SpaIcon from '@mui/icons-material/Spa';
import LocalTaxiIcon from '@mui/icons-material/LocalTaxi';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

const Dashboard = () => {
  const { 
    currentBookings, 
    upcomingBookings, 
    loading: bookingsLoading, 
    error: bookingsError 
  } = useBookings();
  
  const [serviceRequests, setServiceRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Fetch service requests from backend
  useEffect(() => {
    const fetchServiceRequests = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:5000/api/notifications');
        setServiceRequests(response.data.data.notifications || []);
        setError(null);
      } catch (err) {
        console.error('Error fetching service requests:', err);
        setError('Failed to load service requests');
      } finally {
        setLoading(false);
      }
    };
    
    fetchServiceRequests();
    
    // Set up polling to refresh data every 30 seconds
    const interval = setInterval(fetchServiceRequests, 30000);
    
    return () => clearInterval(interval);
  }, []);
  
  // Handle resolving a service request
  const handleResolveRequest = async (id) => {
    try {
      await axios.put(`http://localhost:5000/api/notifications/${id}/resolve`);
      
      // Update local state
      setServiceRequests(prevRequests => 
        prevRequests.map(request => 
          request.id === id ? { ...request, status: 'resolved' } : request
        )
      );
    } catch (err) {
      console.error('Error resolving service request:', err);
      setError('Failed to resolve service request');
    }
  };
  
  // Get service icon based on type
  const getServiceIcon = (type) => {
    switch (type) {
      case 'room_service':
        return <RoomServiceIcon color="primary" />;
      case 'housekeeping':
        return <CleaningServicesIcon color="primary" />;
      case 'maintenance':
        return <BuildIcon color="primary" />;
      case 'concierge':
        return <SupportAgentIcon color="primary" />;
      case 'spa':
        return <SpaIcon color="primary" />;
      case 'transportation':
        return <LocalTaxiIcon color="primary" />;
      default:
        return <RoomServiceIcon color="primary" />;
    }
  };
  
  // Get service label based on type
  const getServiceLabel = (type) => {
    switch (type) {
      case 'room_service':
        return 'Room Service';
      case 'housekeeping':
        return 'Housekeeping';
      case 'maintenance':
        return 'Maintenance';
      case 'concierge':
        return 'Concierge';
      case 'spa':
        return 'Spa & Wellness';
      case 'transportation':
        return 'Transportation';
      default:
        return 'Service Request';
    }
  };
  
  // Get urgency color based on level
  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'low':
        return 'success';
      case 'normal':
        return 'info';
      case 'high':
        return 'warning';
      case 'urgent':
        return 'error';
      default:
        return 'info';
    }
  };
  
  // Format date for display
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Alert Button */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3, height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <AlertButton />
          </Paper>
        </Grid>
        
        {/* Laundry Alert Form */}
        <Grid item xs={12} md={6}>
          <LaundryAlertForm />
        </Grid>
        
        {/* Service Requests */}
        <Grid item xs={12}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Guest Service Requests
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : error ? (
              <Alert severity="error">{error}</Alert>
            ) : serviceRequests.length === 0 ? (
              <Typography variant="body1" sx={{ textAlign: 'center', py: 3 }}>
                No service requests at this time.
              </Typography>
            ) : (
              <List>
                {serviceRequests.map((request) => (
                  <React.Fragment key={request.id}>
                    <ListItem
                      alignItems="flex-start"
                      secondaryAction={
                        request.status === 'pending' ? (
                          <Button
                            variant="contained"
                            color="primary"
                            size="small"
                            onClick={() => handleResolveRequest(request.id)}
                            startIcon={<CheckCircleIcon />}
                          >
                            Resolve
                          </Button>
                        ) : (
                          <Chip
                            label="Resolved"
                            color="success"
                            size="small"
                            icon={<CheckCircleIcon />}
                          />
                        )
                      }
                    >
                      <ListItemIcon>
                        {getServiceIcon(request.serviceType)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="subtitle1">
                              {getServiceLabel(request.serviceType)}
                            </Typography>
                            <Chip
                              label={request.urgency}
                              color={getUrgencyColor(request.urgency)}
                              size="small"
                            />
                          </Box>
                        }
                        secondary={
                          <React.Fragment>
                            <Typography variant="body2" component="span" color="text.primary">
                              Room {request.roomNumber} - {request.guestName}
                            </Typography>
                            <Typography variant="body2" component="div" color="text.secondary">
                              {request.description}
                            </Typography>
                            <Typography variant="caption" component="div" color="text.secondary">
                              {request.preferredTime && `Preferred time: ${request.preferredTime}`}
                            </Typography>
                            <Typography variant="caption" component="div" color="text.secondary">
                              Requested: {formatDate(request.createdAt)}
                            </Typography>
                          </React.Fragment>
                        }
                      />
                    </ListItem>
                    <Divider variant="inset" component="li" />
                  </React.Fragment>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
        
        {/* Current Bookings */}
        <Grid item xs={12} md={6}>
          <BookingList 
            bookings={currentBookings} 
            title="Current Bookings" 
            loading={bookingsLoading} 
            error={bookingsError} 
          />
        </Grid>
        
        {/* Upcoming Bookings */}
        <Grid item xs={12} md={6}>
          <BookingList 
            bookings={upcomingBookings} 
            title="Upcoming Bookings" 
            loading={bookingsLoading} 
            error={bookingsError} 
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;