import React from 'react';
import { Box, Container, Typography, Paper } from '@mui/material';
// import RoomControl from '../components/guest/RoomControl'; // Keep commented until reviewed
import GuestChatbot from '../components/guest/GuestChatbot';
import { useAuth } from '../contexts/AuthContext';

const GuestPage = () => {
  const { currentUser } = useAuth(); // Get current user info if needed

  // Add logout functionality if needed
  // const handleLogout = () => { ... };

  return (
    <Container maxWidth="md" sx={{ mt: 4, display: 'flex', flexDirection: 'column', alignItems: 'center', height: 'calc(100vh - 64px)', // Adjust based on header height if Layout is used
      paddingBottom: '2rem' }}>
      <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ color: '#004466' }}>
        Your Personal Concierge
      </Typography>
      {currentUser && (
         <Typography variant="subtitle1" align="center" gutterBottom sx={{ mb: 2, color: '#555' }}>
           Welcome, {currentUser.firstName}! How can I assist you today?
         </Typography>
      )}

      {/* Make Chatbot the primary element, styled within a Paper component */}
      <Paper elevation={3} sx={{
          width: '100%',
          maxWidth: '800px', // Limit chatbot width
          flexGrow: 1, // Allow chatbot to take available vertical space
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden', // Ensure chatbot content stays within Paper
          bgcolor: '#ffffff' // White background for the chat area
      }}>
        <GuestChatbot />
      </Paper>

      {/* Temporarily commented out RoomControl - review its content */}
      {/* <Box sx={{ width: '100%', mt: 4 }}>
        <Typography variant="h6" gutterBottom>Room Controls</Typography>
        <RoomControl />
      </Box> */}

      {/* Add Logout button here if desired */}
      {/* Example: <Button variant="outlined" onClick={handleLogout} sx={{ mt: 4 }}>Logout</Button> */}
    </Container>
  );
};

export default GuestPage;