import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  Tabs,
  Tab,
  useMediaQuery,
  Divider
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { useAuth } from '../contexts/AuthContext';
import { Navigate, useLocation } from 'react-router-dom';
import ChatIcon from '@mui/icons-material/Chat';
import RoomServiceIcon from '@mui/icons-material/RoomService';
import ServiceRequest from '../components/guest/ServiceRequest';

/**
 * GuestPage component - Main interactive page for hotel guests
 * Provides access to the chatbot and service request functionality
 */
const GuestPage = () => {
  const { currentUser, loading } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [activeTab, setActiveTab] = useState(0);
  const location = useLocation();
  
  // Set active tab based on URL path
  React.useEffect(() => {
    if (location.pathname.includes('/services')) {
      setActiveTab(1);
    } else {
      setActiveTab(0);
    }
  }, [location.pathname]);
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  // Show loading state
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Typography>Loading...</Typography>
      </Box>
    );
  }
  
  // Redirect to login if not authenticated
  if (!currentUser) {
    return <Navigate to="/login" />;
  }
  
  // Placeholder for the chatbot component
  const ChatbotComponent = () => (
    <Paper 
      elevation={3} 
      sx={{ 
        height: isMobile ? 'calc(100vh - 250px)' : '70vh', 
        display: 'flex', 
        flexDirection: 'column',
        borderRadius: 2,
        overflow: 'hidden',
        position: 'relative',
        p: 3,
        textAlign: 'center'
      }}
    >
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
        <ChatIcon sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
        <Typography variant="h4" gutterBottom>
          Hotel AI Assistant
        </Typography>
        <Typography variant="body1" paragraph>
          Hello, {currentUser.firstName || 'Guest'}! How can I help you today?
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          You can ask me about hotel services, local attractions, or request assistance.
        </Typography>
        <Box 
          sx={{ 
            mt: 4, 
            width: '100%', 
            maxWidth: 600, 
            p: 2, 
            border: '1px solid #e0e0e0', 
            borderRadius: 2,
            bgcolor: 'background.paper'
          }}
        >
          <Typography variant="body1" sx={{ fontStyle: 'italic', color: 'text.secondary' }}>
            Try asking:
          </Typography>
          <Divider sx={{ my: 1 }} />
          <Typography variant="body2" paragraph>
            "I need fresh towels for my room"
          </Typography>
          <Typography variant="body2" paragraph>
            "What time does the hotel restaurant open?"
          </Typography>
          <Typography variant="body2" paragraph>
            "Can you recommend nearby attractions?"
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
  
  // Tab panel component
  const TabPanel = (props) => {
    const { children, value, index, ...other } = props;
    return (
      <div
        role="tabpanel"
        hidden={value !== index}
        id={`guest-tabpanel-${index}`}
        aria-labelledby={`guest-tab-${index}`}
        {...other}
        style={{ height: '100%' }}
      >
        {value === index && children}
      </div>
    );
  };
  
  return (
    <Box>
      {/* Page Header */}
      <Paper elevation={2} sx={{ p: 3, mb: 4, borderRadius: 2 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Guest Services
        </Typography>
        <Typography variant="body1">
          Use our AI assistant to chat or submit service requests directly.
        </Typography>
      </Paper>
      
      {/* Mobile Tabs */}
      {isMobile && (
        <Paper sx={{ mb: 2 }}>
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange} 
            variant="fullWidth"
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab 
              icon={<ChatIcon />} 
              label="AI Assistant" 
              id="guest-tab-0"
              aria-controls="guest-tabpanel-0"
            />
            <Tab 
              icon={<RoomServiceIcon />} 
              label="Request Service" 
              id="guest-tab-1"
              aria-controls="guest-tabpanel-1"
            />
          </Tabs>
        </Paper>
      )}
      
      {/* Desktop Layout */}
      {!isMobile ? (
        <Grid container spacing={4}>
          {/* Chatbot */}
          <Grid item xs={12} md={7}>
            <ChatbotComponent />
          </Grid>
          
          {/* Service Request */}
          <Grid item xs={12} md={5}>
            <ServiceRequest />
          </Grid>
        </Grid>
      ) : (
        /* Mobile Layout */
        <Box sx={{ height: 'calc(100vh - 250px)' }}>
          <TabPanel value={activeTab} index={0}>
            <ChatbotComponent />
          </TabPanel>
          
          <TabPanel value={activeTab} index={1}>
            <Box sx={{ height: '100%', overflow: 'auto' }}>
              <ServiceRequest />
            </Box>
          </TabPanel>
        </Box>
      )}
    </Box>
  );
};

export default GuestPage;