import React from 'react';
import { Box, Button, Typography, Container, Paper, Grid } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext'; // Keep for potential auto-redirect if already logged in

const LandingPage = () => {
  const navigate = useNavigate();
  const { currentUser, userRole } = useAuth(); // Assuming useAuth provides role

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
      </Box>
    </Container>
  );
};

export default LandingPage;