import React from 'react';
import { Container, Box, CssBaseline } from '@mui/material';
import Header from './Header';
// Removed: import ChatbotButton from '../chatbot/ChatbotButton';

const Layout = ({ children }) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <CssBaseline />
      <Header />
      <Container component="main" sx={{ flexGrow: 1, py: 3 }}>
        {children}
      </Container>
      {/* Removed: <ChatbotButton /> */}
      <Box
        component="footer"
        sx={{
          py: 3,
          px: 2,
          mt: 'auto',
          backgroundColor: (theme) =>
            theme.palette.mode === 'light'
              ? theme.palette.grey[200]
              : theme.palette.grey[800],
        }}
      >
        <Container maxWidth="sm">
          <Box textAlign="center">
            <Box component="span" sx={{ color: 'text.secondary' }}>
              © {new Date().getFullYear()} Hotel Management System
            </Box>
          </Box>
        </Container>
      </Box>
    </Box>
  );
};

export default Layout;