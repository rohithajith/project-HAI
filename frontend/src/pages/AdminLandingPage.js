import React from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Paper, 
  Button, 
  Card, 
  CardContent, 
  CardActions,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import DashboardIcon from '@mui/icons-material/Dashboard';
import BookIcon from '@mui/icons-material/Book';
import NotificationsIcon from '@mui/icons-material/Notifications';
import WarningIcon from '@mui/icons-material/Warning';
import PeopleIcon from '@mui/icons-material/People';
import HotelIcon from '@mui/icons-material/Hotel';
import MeetingRoomIcon from '@mui/icons-material/MeetingRoom';
import SupportAgentIcon from '@mui/icons-material/SupportAgent';

/**
 * AdminLandingPage component - Main landing page for admin users
 * Provides quick access to all admin features
 */
const AdminLandingPage = () => {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  
  // Quick stats for the dashboard
  const quickStats = [
    { label: 'Current Guests', value: '24', icon: <PeopleIcon color="primary" /> },
    { label: 'Available Rooms', value: '12', icon: <MeetingRoomIcon color="success" /> },
    { label: 'Pending Alerts', value: '3', icon: <WarningIcon color="error" /> },
    { label: 'Staff On Duty', value: '8', icon: <SupportAgentIcon color="info" /> },
  ];
  
  // Main feature cards
  const featureCards = [
    { 
      title: 'Dashboard', 
      description: 'View hotel performance metrics and key statistics', 
      icon: <DashboardIcon fontSize="large" />, 
      path: '/admin/dashboard',
      color: '#1976d2'
    },
    { 
      title: 'Bookings', 
      description: 'Manage reservations, check-ins, and check-outs', 
      icon: <BookIcon fontSize="large" />, 
      path: '/admin/bookings',
      color: '#2e7d32'
    },
    { 
      title: 'Notifications', 
      description: 'Send and manage guest notifications', 
      icon: <NotificationsIcon fontSize="large" />, 
      path: '/admin/notifications',
      color: '#ed6c02'
    },
    { 
      title: 'Alerts', 
      description: 'Handle emergency alerts and staff notifications', 
      icon: <WarningIcon fontSize="large" />, 
      path: '/admin/alerts',
      color: '#d32f2f'
    },
  ];

  return (
    <Box>
      {/* Welcome Header */}
      <Paper elevation={2} sx={{ p: 3, mb: 4, borderRadius: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <HotelIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
          <Typography variant="h4" component="h1">
            Welcome to Hotel Management System
          </Typography>
        </Box>
        
        <Typography variant="h6" gutterBottom>
          Hello, {currentUser?.firstName || 'Admin'}! 
        </Typography>
        
        <Typography variant="body1" color="text.secondary">
          This is your central hub for managing all aspects of the hotel. 
          Use the navigation menu to access different sections or the quick links below.
        </Typography>
      </Paper>
      
      {/* Quick Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {quickStats.map((stat, index) => (
          <Grid item xs={6} md={3} key={index}>
            <Paper 
              elevation={2} 
              sx={{ 
                p: 2, 
                display: 'flex', 
                alignItems: 'center',
                height: '100%',
                borderRadius: 2
              }}
            >
              <Box sx={{ mr: 2 }}>
                {stat.icon}
              </Box>
              <Box>
                <Typography variant="h4" component="div">
                  {stat.value}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {stat.label}
                </Typography>
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>
      
      {/* Main Feature Cards */}
      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        Quick Access
      </Typography>
      
      <Grid container spacing={3}>
        {featureCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card 
              elevation={3} 
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
                  backgroundColor: card.color,
                  color: 'white'
                }}
              >
                {card.icon}
              </Box>
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="h6" component="h2" gutterBottom>
                  {card.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {card.description}
                </Typography>
              </CardContent>
              <CardActions>
                <Button 
                  size="small" 
                  onClick={() => navigate(card.path)}
                  sx={{ ml: 1, mb: 1 }}
                >
                  Access
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
      
      {/* Recent Activity */}
      <Paper elevation={2} sx={{ mt: 4, p: 3, borderRadius: 2 }}>
        <Typography variant="h6" gutterBottom>
          Recent Activity
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <List>
          <ListItem>
            <ListItemIcon>
              <PeopleIcon />
            </ListItemIcon>
            <ListItemText 
              primary="New guest check-in" 
              secondary="Room 302 - John Smith - 10:15 AM" 
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <WarningIcon color="error" />
            </ListItemIcon>
            <ListItemText 
              primary="Maintenance alert" 
              secondary="Room 205 - AC not working - 9:45 AM" 
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <NotificationsIcon />
            </ListItemIcon>
            <ListItemText 
              primary="Laundry service request" 
              secondary="Room 118 - 9:30 AM" 
            />
          </ListItem>
        </List>
      </Paper>
    </Box>
  );
};

export default AdminLandingPage;