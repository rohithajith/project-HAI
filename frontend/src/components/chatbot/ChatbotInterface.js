import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  IconButton,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Send as SendIcon,
  Settings as SettingsIcon,
  Delete as DeleteIcon,
  Info as InfoIcon,
  ArrowDownward as ScrollDownIcon
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import ConsentManager from '../consent/ConsentManager';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

/**
 * ChatbotInterface component for interacting with the hotel AI assistant
 */
const ChatbotInterface = () => {
  const { currentUser } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sessionToken, setSessionToken] = useState('');
  const [showConsentDialog, setShowConsentDialog] = useState(false);
  const [showConsentBanner, setShowConsentBanner] = useState(false);
  const [consentGiven, setConsentGiven] = useState(false);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);

  // Check if user has given consent
  useEffect(() => {
    const checkConsent = async () => {
      if (currentUser) {
        try {
          const response = await axios.get(`${API_URL}/chatbot/consent`);
          
          if (response.data.success) {
            const hasConsent = response.data.consent?.service_improvement || false;
            setConsentGiven(hasConsent);
            setShowConsentBanner(!hasConsent);
          }
        } catch (error) {
          console.error('Error checking consent:', error);
          // Show consent banner if we can't determine consent status
          setShowConsentBanner(true);
        }
      } else {
        // Show consent banner for non-authenticated users
        setShowConsentBanner(true);
      }
    };

    checkConsent();
  }, [currentUser]);

  // Add system message at the beginning
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          role: 'system',
          content: 'Welcome to our hotel AI assistant! How can I help you today?'
        }
      ]);
    }
  }, [messages]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle scroll events to show/hide scroll button
  useEffect(() => {
    const container = messagesContainerRef.current;
    
    const handleScroll = () => {
      if (container) {
        const { scrollTop, scrollHeight, clientHeight } = container;
        const isScrolledUp = scrollHeight - scrollTop - clientHeight > 100;
        setShowScrollButton(isScrolledUp);
      }
    };
    
    if (container) {
      container.addEventListener('scroll', handleScroll);
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, []);

  // Scroll to the bottom of the messages
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Handle sending a message
  const handleSendMessage = async (e) => {
    e?.preventDefault();
    
    if (!input.trim()) return;
    
    const userMessage = {
      role: 'user',
      content: input
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setError('');
    setLoading(true);
    
    try {
      // Prepare history for the API
      const history = messages.map(msg => ({
        role: msg.role === 'system' ? 'system' : (msg.role === 'user' ? 'user' : 'assistant'),
        content: msg.content
      }));
      
      // Send message to API
      const response = await axios.post(`${API_URL}/chatbot`, {
        message: userMessage.content,
        history,
        sessionToken
      });
      
      // Add assistant response to messages
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: response.data.response
        }
      ]);
      
      // Save session token
      if (response.data.sessionToken) {
        setSessionToken(response.data.sessionToken);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setError('Failed to get a response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle consent banner actions
  const handleConsentAction = (action) => {
    if (action === 'accept') {
      setConsentGiven(true);
      setShowConsentBanner(false);
      
      // Save consent if user is authenticated
      if (currentUser) {
        axios.post(`${API_URL}/chatbot/consent`, {
          serviceImprovement: true,
          modelTraining: false,
          analytics: false,
          marketing: false
        }).catch(error => {
          console.error('Error saving consent:', error);
        });
      }
    } else if (action === 'decline') {
      setConsentGiven(false);
      setShowConsentBanner(false);
    } else if (action === 'settings') {
      setShowConsentDialog(true);
    }
  };

  // Clear chat history
  const handleClearChat = () => {
    setMessages([]);
    setSessionToken('');
  };

  // Format message content with line breaks
  const formatMessageContent = (content) => {
    return content.split('\n').map((line, i) => (
      <React.Fragment key={i}>
        {line}
        {i < content.split('\n').length - 1 && <br />}
      </React.Fragment>
    ));
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Paper 
        elevation={2} 
        sx={{ 
          p: 2, 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          borderRadius: '8px 8px 0 0'
        }}
      >
        <Typography variant="h6" component="h2">
          Hotel AI Assistant
        </Typography>
        
        <Box>
          <Tooltip title="Clear chat">
            <IconButton onClick={handleClearChat} color="default">
              <DeleteIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Privacy settings">
            <IconButton onClick={() => setShowConsentDialog(true)} color="primary">
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Paper>
      
      {/* Consent Banner */}
      {showConsentBanner && (
        <Alert 
          severity="info" 
          sx={{ mb: 2 }}
          action={
            <>
              <Button 
                color="inherit" 
                size="small" 
                onClick={() => handleConsentAction('settings')}
              >
                Settings
              </Button>
              <Button 
                color="inherit" 
                size="small" 
                onClick={() => handleConsentAction('decline')}
              >
                Decline
              </Button>
              <Button 
                color="primary" 
                size="small" 
                onClick={() => handleConsentAction('accept')}
              >
                Accept
              </Button>
            </>
          }
        >
          We'd like to collect conversation data to improve our AI assistant. Your data will be handled securely and in accordance with our privacy policy.
        </Alert>
      )}
      
      {/* Messages Container */}
      <Paper 
        elevation={1} 
        ref={messagesContainerRef}
        sx={{ 
          flex: 1, 
          overflow: 'auto', 
          p: 2,
          display: 'flex',
          flexDirection: 'column',
          bgcolor: 'background.default'
        }}
      >
        <List sx={{ width: '100%', pt: 0 }}>
          {messages.map((message, index) => (
            <ListItem
              key={index}
              alignItems="flex-start"
              sx={{
                flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
                px: 1,
                py: 0.5
              }}
            >
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  maxWidth: '80%',
                  bgcolor: message.role === 'user' ? 'primary.light' : 'background.paper',
                  color: message.role === 'user' ? 'primary.contrastText' : 'text.primary',
                  borderRadius: message.role === 'user' 
                    ? '20px 20px 5px 20px' 
                    : '20px 20px 20px 5px'
                }}
              >
                <ListItemText
                  primary={message.role === 'system' ? 'Hotel AI' : (message.role === 'user' ? 'You' : 'Hotel AI')}
                  secondary={formatMessageContent(message.content)}
                  primaryTypographyProps={{
                    fontWeight: 'bold',
                    variant: 'body2'
                  }}
                  secondaryTypographyProps={{
                    variant: 'body1',
                    color: message.role === 'user' ? 'inherit' : 'text.primary'
                  }}
                />
              </Paper>
            </ListItem>
          ))}
          
          {/* Loading indicator */}
          {loading && (
            <ListItem alignItems="flex-start">
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  maxWidth: '80%',
                  bgcolor: 'background.paper',
                  borderRadius: '20px 20px 20px 5px'
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  <Typography variant="body2">Hotel AI is typing...</Typography>
                </Box>
              </Paper>
            </ListItem>
          )}
          
          {/* Error message */}
          {error && (
            <ListItem>
              <Alert severity="error" sx={{ width: '100%' }}>
                {error}
              </Alert>
            </ListItem>
          )}
          
          {/* Invisible element to scroll to */}
          <div ref={messagesEndRef} />
        </List>
        
        {/* Scroll down button */}
        {showScrollButton && (
          <Box sx={{ position: 'sticky', bottom: 16, alignSelf: 'center' }}>
            <Tooltip title="Scroll to bottom">
              <IconButton
                color="primary"
                onClick={scrollToBottom}
                sx={{ 
                  bgcolor: 'background.paper',
                  boxShadow: 2,
                  '&:hover': { bgcolor: 'background.paper' }
                }}
              >
                <ScrollDownIcon />
              </IconButton>
            </Tooltip>
          </Box>
        )}
      </Paper>
      
      {/* Input Area */}
      <Paper 
        component="form" 
        onSubmit={handleSendMessage}
        elevation={2} 
        sx={{ 
          p: 2, 
          display: 'flex', 
          alignItems: 'center',
          borderRadius: '0 0 8px 8px'
        }}
      >
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          sx={{ mr: 1 }}
          InputProps={{
            sx: { borderRadius: 4 }
          }}
        />
        
        <Button
          variant="contained"
          color="primary"
          endIcon={<SendIcon />}
          disabled={!input.trim() || loading}
          type="submit"
          sx={{ borderRadius: 4 }}
        >
          Send
        </Button>
      </Paper>
      
      {/* Consent Manager Dialog */}
      <Dialog
        open={showConsentDialog}
        onClose={() => setShowConsentDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Privacy Settings</DialogTitle>
        <DialogContent>
          <ConsentManager onClose={() => setShowConsentDialog(false)} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowConsentDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ChatbotInterface;