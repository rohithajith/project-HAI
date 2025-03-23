import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  IconButton,
  Divider,
  Tooltip,
  Zoom,
  Fade,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Send as SendIcon,
  Settings as SettingsIcon,
  Delete as DeleteIcon,
  BugReport as BugIcon,
  ArrowDownward as ScrollDownIcon,
  Spa as SpaIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { useAuth } from '../../../contexts/AuthContext';
import ConsentManager from '../../consent/ConsentManager';
import axios from 'axios';

// Import custom components
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import DebugPanel from './DebugPanel';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

// Styled components
const ChatContainer = styled(Box)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  position: 'relative',
}));

const ChatHeader = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  borderRadius: '12px 12px 0 0',
  backgroundColor: theme.palette.primary.dark,
  color: theme.palette.primary.contrastText,
  boxShadow: theme.shadows[3],
  zIndex: 10,
}));

const MessagesContainer = styled(Paper)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(2),
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: theme.palette.background.default,
  backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px)',
  backgroundSize: '20px 20px',
  position: 'relative',
}));

const InputContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  display: 'flex',
  alignItems: 'center',
  borderRadius: '0 0 12px 12px',
  backgroundColor: theme.palette.background.paper,
  boxShadow: theme.shadows[3],
  zIndex: 10,
}));

const ScrollButton = styled(IconButton)(({ theme }) => ({
  position: 'absolute',
  bottom: theme.spacing(2),
  right: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
  boxShadow: theme.shadows[3],
  '&:hover': {
    backgroundColor: theme.palette.background.default,
  },
}));

const StyledTextField = styled(TextField)(({ theme, isEmpty }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: theme.spacing(3),
    transition: 'all 0.3s ease',
    ...(isEmpty && {
      animation: 'pulse 2s infinite',
      '@keyframes pulse': {
        '0%': {
          boxShadow: '0 0 0 0 rgba(25, 118, 210, 0.4)',
        },
        '70%': {
          boxShadow: '0 0 0 6px rgba(25, 118, 210, 0)',
        },
        '100%': {
          boxShadow: '0 0 0 0 rgba(25, 118, 210, 0)',
        },
      },
    }),
  },
}));

/**
 * EnhancedChatInterface component for the guest UI
 * Provides an improved chat experience with animations and debugging features
 */
const EnhancedChatInterface = () => {
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
  const [showDebugPanel, setShowDebugPanel] = useState(false);
  const [debugInfo, setDebugInfo] = useState({
    apiCalls: [],
    conversationState: null
  });
  const [newMessageId, setNewMessageId] = useState(null);
  
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
          id: 'welcome-message',
          role: 'system',
          content: 'Welcome to our hotel AI assistant! How can I help you today?',
          timestamp: new Date().toISOString()
        }
      ]);
    }
  }, [messages]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
    
    // Mark new message as seen after animation completes
    if (newMessageId) {
      const timer = setTimeout(() => {
        setNewMessageId(null);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [messages, newMessageId]);

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

  // Add API call to debug info
  const addApiCallToDebug = (callInfo) => {
    setDebugInfo(prev => ({
      ...prev,
      apiCalls: [...prev.apiCalls, callInfo]
    }));
  };

  // Update API call in debug info
  const updateApiCallInDebug = (index, updates) => {
    setDebugInfo(prev => {
      const updatedCalls = [...prev.apiCalls];
      updatedCalls[index] = { ...updatedCalls[index], ...updates };
      return {
        ...prev,
        apiCalls: updatedCalls
      };
    });
  };

  // Clear debug info
  const clearDebugInfo = () => {
    setDebugInfo({
      apiCalls: [],
      conversationState: null
    });
  };

  // Handle sending a message
  const handleSendMessage = async (e) => {
    e?.preventDefault();
    
    if (!input.trim()) return;
    
    const messageId = `msg-${Date.now()}`;
    const userMessage = {
      id: messageId,
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setError('');
    setLoading(true);
    setNewMessageId(messageId);
    
    // Add API call to debug info
    const apiCallIndex = debugInfo.apiCalls.length;
    addApiCallToDebug({
      type: 'Send Message',
      status: 'pending',
      startTime: new Date().toISOString(),
      request: { message: userMessage.content }
    });
    
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
      
      // Update API call in debug info
      updateApiCallInDebug(apiCallIndex, {
        status: 'success',
        endTime: new Date().toISOString(),
        response: response.data
      });
      
      // Update conversation state in debug info
      setDebugInfo(prev => ({
        ...prev,
        conversationState: {
          sessionToken: response.data.sessionToken || sessionToken,
          messageCount: messages.length + 1,
          lastMessageTime: new Date().toISOString()
        }
      }));
      
      // Add assistant response to messages
      const assistantMessageId = `msg-${Date.now()}`;
      setMessages(prev => [
        ...prev,
        {
          id: assistantMessageId,
          role: 'assistant',
          content: response.data.response,
          timestamp: new Date().toISOString()
        }
      ]);
      setNewMessageId(assistantMessageId);
      
      // Save session token
      if (response.data.sessionToken) {
        setSessionToken(response.data.sessionToken);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setError('Failed to get a response. Please try again.');
      
      // Update API call in debug info with error
      updateApiCallInDebug(apiCallIndex, {
        status: 'error',
        endTime: new Date().toISOString(),
        error: error.response?.data?.message || error.message
      });
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
    clearDebugInfo();
  };

  // Toggle debug panel
  const toggleDebugPanel = () => {
    setShowDebugPanel(!showDebugPanel);
  };

  return (
    <ChatContainer>
      {/* Header */}
      <ChatHeader elevation={3}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <SpaIcon sx={{ mr: 1.5 }} />
          <Typography variant="h6" component="h2">
            Hotel AI Assistant
          </Typography>
        </Box>
        
        <Box>
          <Tooltip title="Clear chat">
            <IconButton onClick={handleClearChat} sx={{ color: 'rgba(255,255,255,0.7)' }}>
              <DeleteIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Debug panel">
            <IconButton 
              onClick={toggleDebugPanel} 
              sx={{ 
                color: showDebugPanel ? 'primary.light' : 'rgba(255,255,255,0.7)',
                bgcolor: showDebugPanel ? 'rgba(255,255,255,0.2)' : 'transparent'
              }}
            >
              <BugIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Privacy settings">
            <IconButton onClick={() => setShowConsentDialog(true)} sx={{ color: 'rgba(255,255,255,0.7)' }}>
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </ChatHeader>
      
      {/* Consent Banner */}
      {showConsentBanner && (
        <Fade in={showConsentBanner}>
          <Alert 
            severity="info" 
            sx={{ borderRadius: 0 }}
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
        </Fade>
      )}
      
      {/* Messages Container */}
      <MessagesContainer 
        elevation={0} 
        ref={messagesContainerRef}
      >
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            role={message.role}
            content={message.content}
            timestamp={message.timestamp}
            isNew={message.id === newMessageId}
          />
        ))}
        
        {/* Loading indicator */}
        {loading && <TypingIndicator />}
        
        {/* Invisible element to scroll to */}
        <div ref={messagesEndRef} />
        
        {/* Scroll down button */}
        <Zoom in={showScrollButton}>
          <ScrollButton
            color="primary"
            onClick={scrollToBottom}
            size="small"
          >
            <ScrollDownIcon />
          </ScrollButton>
        </Zoom>
      </MessagesContainer>
      
      {/* Input Area */}
      <InputContainer 
        component="form" 
        onSubmit={handleSendMessage}
        elevation={3}
      >
        <StyledTextField
          fullWidth
          variant="outlined"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          sx={{ mr: 1 }}
          isEmpty={!input.trim() && !loading}
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
          sx={{ 
            borderRadius: 4,
            px: 3,
            py: 1.5,
            transition: 'all 0.2s ease',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: 4
            }
          }}
        >
          Send
        </Button>
      </InputContainer>
      
      {/* Debug Panel */}
      {showDebugPanel && (
        <DebugPanel 
          debugInfo={debugInfo} 
          hasErrors={debugInfo.apiCalls.some(call => call.status === 'error')}
          onClear={clearDebugInfo}
        />
      )}
      
      {/* Error Snackbar */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError('')}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setError('')} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
      
      {/* Consent Manager Dialog */}
      <ConsentManager 
        open={showConsentDialog}
        onClose={() => setShowConsentDialog(false)}
      />
    </ChatContainer>
  );
};

export default EnhancedChatInterface;