import React from 'react';
import { Box, Button, Typography, Grid, Paper, Container } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ChatbotInterface from '../components/chatbot/ChatbotInterface';

const LandingPage = () => {
  const navigate = useNavigate();
  const { currentUser } = useAuth();

  const handleRoomControlClick = () => {
    // Placeholder for room control functionality
    alert("Room control functionality will be implemented here.");
  };

  const handleEmergencyClick = () => {
    navigate('/alerts');
  };

  const handleLoginClick = () => {
    navigate('/login');
  };

  const handleRegisterClick = () => {
    navigate('/register');
  };

  const handleDashboardClick = () => {
    navigate('/dashboard');
  };

  return (
    <Container maxWidth="lg">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '80vh',
          padding: 4,
        }}
      >
        <Typography variant="h2" component="h1" gutterBottom align="center">
          Welcome to Hotel Management System
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom align="center" sx={{ mb: 4 }}>
          Enterprise-Level Hotel Management Solution
        </Typography>

        {currentUser ? (
          // User is logged in
          <Paper elevation={3} sx={{ p: 4, width: '100%', mb: 4 }}>
            <Typography variant="h5" gutterBottom>
              Welcome back, {currentUser.firstName}!
            </Typography>
            <Button
              fullWidth
              variant="contained"
              size="large"
              onClick={handleDashboardClick}
              sx={{ mt: 2 }}
            >
              Go to Dashboard
            </Button>
          </Paper>
        ) : (
          // User is not logged in
          <Paper elevation={3} sx={{ p: 4, width: '100%', mb: 4 }}>
            <Typography variant="h5" gutterBottom align="center">
              Please log in or register to access the system
            </Typography>
            <Grid container spacing={2} sx={{ mt: 2 }}>
              <Grid item xs={12} sm={6}>
                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  onClick={handleLoginClick}
                >
                  Login
                </Button>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Button
                  fullWidth
                  variant="outlined"
                  size="large"
                  onClick={handleRegisterClick}
                >
                  Register
                </Button>
              </Grid>
            </Grid>
          </Paper>
        )}

        <Typography variant="h4" component="h2" gutterBottom sx={{ mt: 4 }}>
          Guest Services
        </Typography>

        <Grid container spacing={3} justifyContent="center">
          <Grid item xs={12} sm={6} md={4}>
            <Button
              fullWidth
              variant="contained"
              size="large"
              onClick={handleRoomControlClick}
            >
              Room Control
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <ChatbotInterface />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Button
              fullWidth
              variant="contained"
              size="large"
              color="error"
              onClick={handleEmergencyClick}
            >
              SOS Emergency
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default LandingPage;