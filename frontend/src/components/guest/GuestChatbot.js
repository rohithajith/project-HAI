import React from 'react';
import { Box, Typography, TextField, Button } from '@mui/material';

const GuestChatbot = () => {
  // Placeholder state and functions for chatbot interaction
  const [message, setMessage] = React.useState('');
  const [chatHistory, setChatHistory] = React.useState([]);

  const handleSendMessage = () => {
    if (message.trim()) {
      // Placeholder: Add message to history and clear input
      // In reality, this would send the message to the backend/local model
      setChatHistory([...chatHistory, { sender: 'user', text: message }]);
      setMessage('');
      // Placeholder for bot response
      setTimeout(() => {
        setChatHistory(prev => [...prev, { sender: 'bot', text: 'Connecting to local model...' }]);
      }, 500);
    }
  };

  return (
    <Box sx={{ p: 2, border: '1px dashed grey', height: '400px', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h6" gutterBottom>Chatbot</Typography>
      <Box sx={{ flexGrow: 1, overflowY: 'auto', mb: 2, border: '1px solid #ccc', p: 1 }}>
        {chatHistory.map((msg, index) => (
          <Typography key={index} align={msg.sender === 'user' ? 'right' : 'left'}>
            <strong>{msg.sender === 'user' ? 'You' : 'Bot'}:</strong> {msg.text}
          </Typography>
        ))}
      </Box>
      <Box sx={{ display: 'flex' }}>
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          placeholder="Type your message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
        />
        <Button variant="contained" onClick={handleSendMessage} sx={{ ml: 1 }}>Send</Button>
      </Box>
    </Box>
  );
};

export default GuestChatbot;