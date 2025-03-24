import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Button,
  Card,
  CardContent
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ChatIcon from '@mui/icons-material/Chat';
import RoomServiceIcon from '@mui/icons-material/RoomService';
import CleaningServicesIcon from '@mui/icons-material/CleaningServices';
import SpaIcon from '@mui/icons-material/Spa';
import LocalTaxiIcon from '@mui/icons-material/LocalTaxi';

/**
 * GuestLandingPage component - Landing page specifically for hotel guests
 * Provides quick access to guest services and chatbot
 */
const GuestLandingPage = () => {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  
  // Service cards for quick access
  const serviceCards = [
    {
      title: 'AI Concierge',
      description: 'Chat with our AI assistant for information or to request services',
      icon: <ChatIcon fontSize="large" color="primary" />,
      action: 'Start Chatting',
      path: '/guest/chatbot'
    },
    {
      title: 'Room Service',
      description: 'Order food and beverages directly to your room',
      icon: <RoomServiceIcon fontSize="large" color="primary" />,
      action: 'Order Now',
      path: '/guest/services'
    },
    {
      title: 'Housekeeping',
      description: 'Request room cleaning or additional amenities',
      icon: <CleaningServicesIcon fontSize="large" color="primary" />,
      action: 'Request Service',
      path: '/guest/services'
    },
    {
      title: 'Spa & Wellness',
      description: 'Book spa treatments and wellness activities',
      icon: <SpaIcon fontSize="large" color="primary" />,
      action: 'Book Appointment',
      path: '/guest/services'
    },
    {
      title: 'Transportation',
      description: 'Arrange airport transfers or local transportation',
      icon: <LocalTaxiIcon fontSize="large" color="primary" />,
      action: 'Arrange Ride',
      path: '/guest/services'
    }
  ];

  return (
    <Box>
      {/* Welcome Header */}
      <Paper elevation={2} sx={{ p: 3, mb: 4, borderRadius: 2 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome to Your Luxury Stay
        </Typography>
        <Typography variant="h6" gutterBottom>
          Hello, {currentUser?.firstName || 'Guest'}!
        </Typography>
        <Typography variant="body1">
          We're delighted to have you with us. Explore our services below or chat with our AI assistant for personalized help.
        </Typography>
      </Paper>
      
      {/* Featured Service - Chatbot */}
      <Paper 
        elevation={3} 
        sx={{ 
          p: 3, 
          mb: 4, 
          borderRadius: 2,
          background: 'linear-gradient(45deg, #1976d2 30%, #42a5f5 90%)',
          color: 'white'
        }}
      >
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={8}>
            <Typography variant="h5" gutterBottom>
              Meet Your AI Concierge
            </Typography>
            <Typography variant="body1" paragraph>
              Our AI assistant is available 24/7 to answer your questions, provide information about the hotel and local attractions, or help you request services.
            </Typography>
            <Button 
              variant="contained" 
              color="secondary"
              size="large"
              startIcon={<ChatIcon />}
              onClick={() => navigate('/guest/chatbot')}
              sx={{ mt: 1 }}
            >
              Start Chatting Now
            </Button>
          </Grid>
          <Grid item xs={12} md={4} sx={{ textAlign: 'center' }}>
            <ChatIcon sx={{ fontSize: 100, opacity: 0.9 }} />
          </Grid>
        </Grid>
      </Paper>
      
      {/* Services Grid */}
      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        Hotel Services
      </Typography>
      
      <Grid container spacing={3}>
        {serviceCards.map((service, index) => (
          index !== 0 && (  // Skip the first item (AI Concierge) as it's featured above
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card 
                elevation={2} 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  borderRadius: 2,
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-5px)',
                    boxShadow: 6
                  }
                }}
              >
                <Box 
                  sx={{ 
                    p: 2, 
                    display: 'flex', 
                    justifyContent: 'center',
                    bgcolor: 'background.paper'
                  }}
                >
                  {service.icon}
                </Box>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography variant="h6" component="h3" gutterBottom>
                    {service.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {service.description}
                  </Typography>
                </CardContent>
                <Box sx={{ p: 2, pt: 0 }}>
                  <Button 
                    fullWidth
                    variant="outlined" 
                    color="primary"
                    onClick={() => navigate(service.path)}
                  >
                    {service.action}
                  </Button>
                </Box>
              </Card>
            </Grid>
          )
        ))}
      </Grid>
      
      {/* Room Information */}
      <Paper elevation={2} sx={{ p: 3, mt: 4, borderRadius: 2 }}>
        <Typography variant="h5" gutterBottom>
          Your Stay Information
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="body1">
              <strong>Room:</strong> {currentUser?.profile?.room_number || '301 (Deluxe Suite)'}
            </Typography>
            <Typography variant="body1">
              <strong>Check-in:</strong> {currentUser?.profile?.check_in || 'March 23, 2025'}
            </Typography>
            <Typography variant="body1">
              <strong>Check-out:</strong> {currentUser?.profile?.check_out || 'March 27, 2025'}
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="body1">
              <strong>Wi-Fi Network:</strong> LuxuryHotel_Guest
            </Typography>
            <Typography variant="body1">
              <strong>Wi-Fi Password:</strong> LuxStay2025
            </Typography>
            <Typography variant="body1">
              <strong>Room Service Hours:</strong> 24/7
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default GuestLandingPage;