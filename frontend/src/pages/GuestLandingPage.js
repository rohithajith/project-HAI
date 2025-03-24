import React from 'react';
import { Box, Container, Typography } from '@mui/material';
import ChatbotInterface from '../components/chatbot/ChatbotInterface';
import RoomControl from '../components/roomControl/RoomControl';

const GuestLandingPage = () => {
  return (
    <Container maxWidth="lg">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          padding: 4,
        }}
      >
        <Typography variant="h2" component="h1" gutterBottom align="center">
          Welcome to Hotel Management System
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom align="center" sx={{ mb: 4 }}>
          Guest Services
        </Typography>

        <Box sx={{ width: '100%', mb: 4 }}>
          <ChatbotInterface />
        </Box>

        <Box sx={{ width: '100%' }}>
          <RoomControl />
        </Box>
      </Box>
    </Container>
  );
};

export default GuestLandingPage;