import React, { useState, useEffect, useRef } from 'react';
import { Box, Typography, TextField, Button, CircularProgress, Alert } from '@mui/material';
import api from '../../services/api'; // Assuming api service exists for base URL etc.

const GuestChatbot = () => {
  const [message, setMessage] = useState('');
  // Use the format expected by the backend: { role: 'user'/'assistant', content: '...' }
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const chatBoxRef = useRef(null); // To scroll to bottom

  // Function to scroll chat to the bottom
  const scrollToBottom = () => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  };

  // Scroll to bottom whenever chatHistory changes
  useEffect(() => {
    scrollToBottom();
  }, [chatHistory]);

  const handleSendMessage = async () => {
    if (!message.trim() || isLoading) {
      return; // Prevent sending empty messages or multiple requests
    }

    const userMessage = { role: 'user', content: message };
    // Add user message immediately to UI
    setChatHistory(prev => [...prev, userMessage]);
    setMessage(''); // Clear input
    setIsLoading(true);
    setError(null);

    // Prepare history for backend (limit length if necessary)
    const historyForBackend = [...chatHistory, userMessage]; // Include the latest user message

    try {
      // Use the api service if available, otherwise use fetch directly
      const response = await api.post('/chatbot', {
          message: userMessage.content,
          history: historyForBackend // Send the updated history
      });

      // Assuming backend returns { response: "bot message text" }
      if (response.data && response.data.response) {
        const botMessage = { role: 'assistant', content: response.data.response };
        setChatHistory(prev => [...prev, botMessage]);
      } else {
        throw new Error('Invalid response format from server');
      }

    } catch (err) {
      console.error('Error sending message:', err);
      const errorMessage = err.response?.data?.error || err.message || 'Failed to get response from the concierge.';
      setError(errorMessage);
      // Optionally add an error message to chat history
      setChatHistory(prev => [...prev, { role: 'assistant', content: `Sorry, I encountered an error: ${errorMessage}` }]);
    } finally {
      setIsLoading(false);
      // Ensure scroll happens after state update
      setTimeout(scrollToBottom, 0);
    }
  };

  return (
    // Adjusted Box styling to fill parent Paper component
    <Box sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Removed fixed height and border from original Box */}
      <Typography variant="h6" gutterBottom sx={{ textAlign: 'center', color: '#333' }}>
          Concierge Chat
      </Typography>
      {error && <Alert severity="error" sx={{ mb: 1 }}>{error}</Alert>}
      {/* Chat history area */}
      <Box
        ref={chatBoxRef}
        sx={{
          flexGrow: 1,
          overflowY: 'auto',
          mb: 2,
          border: '1px solid #e0e0e0',
          p: 1.5,
          borderRadius: '4px',
          bgcolor: '#f9f9f9' // Slightly off-white background for chat area
        }}
      >
        {chatHistory.map((msg, index) => (
          <Box
            key={index}
            sx={{
              mb: 1,
              p: 1,
              borderRadius: '8px',
              bgcolor: msg.role === 'user' ? '#007bff' : '#e9ecef',
              color: msg.role === 'user' ? '#fff' : '#333',
              marginLeft: msg.role === 'user' ? 'auto' : '0',
              marginRight: msg.role === 'user' ? '0' : 'auto',
              maxWidth: '80%',
              wordWrap: 'break-word'
            }}
          >
            {/* Removed sender label for cleaner look */}
            {msg.content}
          </Box>
        ))}
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 1 }}>
            <CircularProgress size={24} />
          </Box>
        )}
      </Box>
      {/* Input area */}
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          placeholder="Ask me anything..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          disabled={isLoading}
          sx={{ bgcolor: '#fff' }} // Ensure input background is white
        />
        <Button
          variant="contained"
          onClick={handleSendMessage}
          disabled={isLoading}
          sx={{ ml: 1 }}
        >
          Send
        </Button>
      </Box>
    </Box>
  );
};

export default GuestChatbot;