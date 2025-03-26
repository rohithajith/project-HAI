import React from 'react';
import { Box, Button, Typography, Container, Paper, Grid } from '@mui/material';
import { useNavigate } from 'react-router-dom';
<<<<<<< HEAD
import { useAuth } from '../contexts/AuthContext'; // Keep for potential auto-redirect if already logged in
=======
import { useAuth } from '../contexts/AuthContext';
import ChatbotInterface from '../components/chatbot/ChatbotInterface';
>>>>>>> e1460d6789cb070325e1e5df2a7091b6fedf1639

const LandingPage = () => {
  const navigate = useNavigate();
  const { currentUser, userRole } = useAuth(); // Assuming useAuth provides role

<<<<<<< HEAD
  // Optional: Redirect if already logged in
  React.useEffect(() => {
    if (currentUser) {
      if (userRole === 'guest') { // Assuming 'guest' role exists
        navigate('/guest');
      } else if (['admin', 'manager', 'staff'].includes(userRole)) {
        navigate('/admin/dashboard');
      }
      // Add handling for other roles or default redirect if needed
    }
  }, [currentUser, userRole, navigate]);
  console.log("LandingPage: currentUser:", currentUser, "userRole:", userRole);

  const handleAdminLogin = () => {
    // Navigate to a login page, potentially passing a target role or redirect path
    navigate('/login', { state: { role: 'admin' } });
  };

  const handleGuestLogin = () => {
    // Navigate to a login page, potentially passing a target role or redirect path
    navigate('/login', { state: { role: 'guest' } });
=======
  const handleRoomControlClick = () => {
    // Placeholder for room control functionality
    alert("Room control functionality will be implemented here.");
>>>>>>> e1460d6789cb070325e1e5df2a7091b6fedf1639
  };

  // Render nothing or a loading indicator if already logged in and redirecting
  if (currentUser) {
    return (
      <Container maxWidth="sm" sx={{ textAlign: 'center', mt: 8 }}>
        <Typography variant="h5">Redirecting...</Typography>
        {/* Or add a loading spinner */}
      </Container>
    );
  }

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Typography component="h1" variant="h4" gutterBottom>
          Hotel Management System
        </Typography>
<<<<<<< HEAD
        <Paper elevation={3} sx={{ p: 4, mt: 3, width: '100%' }}>
          <Typography component="h2" variant="h5" align="center" gutterBottom>
            Select Login Type
          </Typography>
          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid item xs={12}>
              <Button
                fullWidth
                variant="contained"
                size="large"
                onClick={handleAdminLogin}
                sx={{ py: 2 }}
              >
                Admin / Staff Login
              </Button>
            </Grid>
            <Grid item xs={12}>
              <Button
                fullWidth
                variant="outlined"
                size="large"
                onClick={handleGuestLogin}
                sx={{ py: 2 }}
              >
                Guest Login
              </Button>
            </Grid>
          </Grid>
        </Paper>
=======

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
>>>>>>> e1460d6789cb070325e1e5df2a7091b6fedf1639
      </Box>
    </Container>
  );
};

export default LandingPage;