import React, { useState } from 'react';
import { Box, Container, Tabs, Tab, Typography } from '@mui/material';
import RoomControl from '../components/guest/RoomControl';
import GuestChatbot from '../components/guest/GuestChatbot';
import { useAuth } from '../contexts/AuthContext'; // Assuming guest auth uses the same context for now

// TabPanel component (same as used in previous LandingPage)
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`guest-tabpanel-${index}`}
      aria-labelledby={`guest-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ pt: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index) {
  return {
    id: `guest-tab-${index}`,
    'aria-controls': `guest-tabpanel-${index}`,
  };
}

const GuestPage = () => {
  const [activeTab, setActiveTab] = useState(0); // 0 for Room Control, 1 for Chatbot
  const { currentUser } = useAuth(); // Get current user info if needed

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Add logout functionality if needed
  // const handleLogout = () => { ... };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom align="center">
        Guest Services
      </Typography>
      {currentUser && (
         <Typography variant="subtitle1" align="center" gutterBottom>
           Welcome, {currentUser.firstName}! {/* Display guest name */}
         </Typography>
      )}
      <Box sx={{ width: '100%', borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={activeTab} onChange={handleTabChange} aria-label="Guest service tabs" centered>
          <Tab label="Room Control" {...a11yProps(0)} />
          <Tab label="Chatbot" {...a11yProps(1)} />
        </Tabs>
      </Box>
      <TabPanel value={activeTab} index={0}>
        <RoomControl />
      </TabPanel>
      <TabPanel value={activeTab} index={1}>
        <GuestChatbot />
      </TabPanel>
      {/* Add Logout button here if desired */}
    </Container>
  );
};

export default GuestPage;