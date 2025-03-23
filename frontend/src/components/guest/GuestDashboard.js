import React, { useState } from 'react';
import { 
  Box, 
  Grid, 
  Container, 
  Paper, 
  Typography, 
  useMediaQuery, 
  Tabs, 
  Tab, 
  Fade,
  IconButton,
  Tooltip
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { 
  Chat as ChatIcon, 
  ThermostatAuto as ThermostatIcon,
  ExpandLess as ExpandIcon,
  ExpandMore as CollapseIcon
} from '@mui/icons-material';

// Import components
import GuestHeader from '../common/GuestHeader';
import RoomControlCard from './RoomControlCard';
import EnhancedChatInterface from './EnhancedChatbot/EnhancedChatInterface';

/**
 * GuestDashboard component - Main dashboard for guest users
 * Displays room controls and enhanced chatbot interface
 */
const GuestDashboard = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [activeTab, setActiveTab] = useState(0);
  const [chatExpanded, setChatExpanded] = useState(!isMobile);

  // Handle tab change for mobile view
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Toggle chat expansion
  const toggleChatExpansion = () => {
    setChatExpanded(!chatExpanded);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <GuestHeader />
      
      <Container maxWidth="xl" sx={{ flexGrow: 1, py: 3 }}>
        <Typography 
          variant="h4" 
          component="h1" 
          sx={{ 
            mb: 3, 
            fontWeight: 'bold',
            color: 'text.primary',
            textAlign: { xs: 'center', md: 'left' }
          }}
        >
          Welcome to Your Luxury Suite
        </Typography>
        
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
                icon={<ThermostatIcon />} 
                label="Room Controls" 
                id="room-controls-tab"
                aria-controls="room-controls-panel"
              />
              <Tab 
                icon={<ChatIcon />} 
                label="AI Assistant" 
                id="chat-tab"
                aria-controls="chat-panel"
              />
            </Tabs>
          </Paper>
        )}
        
        {/* Desktop and Tablet Layout */}
        {!isMobile ? (
          <Grid container spacing={3}>
            {/* Room Controls */}
            <Grid item xs={12} md={chatExpanded ? 5 : 8} lg={chatExpanded ? 4 : 8}>
              <RoomControlCard />
            </Grid>
            
            {/* Chat Interface */}
            <Grid item xs={12} md={chatExpanded ? 7 : 4} lg={chatExpanded ? 8 : 4}>
              <Paper 
                elevation={3} 
                sx={{ 
                  height: '70vh', 
                  display: 'flex', 
                  flexDirection: 'column',
                  borderRadius: 2,
                  overflow: 'hidden',
                  position: 'relative'
                }}
              >
                <Box 
                  sx={{ 
                    position: 'absolute', 
                    top: 8, 
                    left: 8, 
                    zIndex: 10 
                  }}
                >
                  <Tooltip title={chatExpanded ? "Collapse chat" : "Expand chat"}>
                    <IconButton 
                      onClick={toggleChatExpansion}
                      size="small"
                      sx={{ 
                        bgcolor: 'background.paper', 
                        boxShadow: 2,
                        '&:hover': { bgcolor: 'background.paper' }
                      }}
                    >
                      {chatExpanded ? <CollapseIcon /> : <ExpandIcon />}
                    </IconButton>
                  </Tooltip>
                </Box>
                <EnhancedChatInterface />
              </Paper>
            </Grid>
          </Grid>
        ) : (
          /* Mobile Layout */
          <Box sx={{ mt: 2 }}>
            {/* Room Controls Panel */}
            <Fade in={activeTab === 0} unmountOnExit>
              <Box 
                role="tabpanel"
                id="room-controls-panel"
                aria-labelledby="room-controls-tab"
                hidden={activeTab !== 0}
              >
                <RoomControlCard />
              </Box>
            </Fade>
            
            {/* Chat Interface Panel */}
            <Fade in={activeTab === 1} unmountOnExit>
              <Box 
                role="tabpanel"
                id="chat-panel"
                aria-labelledby="chat-tab"
                hidden={activeTab !== 1}
                sx={{ height: 'calc(100vh - 200px)' }}
              >
                <Paper 
                  elevation={3} 
                  sx={{ 
                    height: '100%', 
                    display: 'flex', 
                    flexDirection: 'column',
                    borderRadius: 2,
                    overflow: 'hidden'
                  }}
                >
                  <EnhancedChatInterface />
                </Paper>
              </Box>
            </Fade>
          </Box>
        )}
      </Container>
      
      <Box 
        component="footer" 
        sx={{ 
          py: 2, 
          mt: 'auto', 
          textAlign: 'center',
          bgcolor: 'background.paper',
          borderTop: 1,
          borderColor: 'divider'
        }}
      >
        <Typography variant="body2" color="text.secondary">
          © {new Date().getFullYear()} Luxury Hotel Experience. All rights reserved.
        </Typography>
      </Box>
    </Box>
  );
};

export default GuestDashboard;