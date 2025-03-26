import React, { useState, useEffect } from 'react';
import { notificationsApi } from '../services/api';
import './ChatbotInterface.css';

const ChatbotInterface = ({ roomNumber, onServiceRequest }) => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // Initialize with welcome message
  useEffect(() => {
    setMessages([{ sender: 'bot', text: 'Hello! How can I assist you today?' }]);
  }, []);

  const handleSend = async () => {
    if (!inputText.trim()) return;

    const userMessage = { sender: 'user', text: inputText };
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);

    try {
      const response = await notificationsApi.create({
        message: inputText,
        queryType: "chat",
        roomNumber,
        history: messages
          .filter(msg => msg.sender === 'user' || msg.sender === 'bot')
          .map(msg => ({
            role: msg.sender === 'user' ? 'user' : 'assistant',
            content: msg.text
          }))
      });

      const botResponse = { sender: 'bot', text: response.data.response };
      setMessages(prev => [...prev, botResponse]);

      if (response.data.serviceRequest) {
        onServiceRequest({
          type: response.data.serviceType,
          message: inputText,
          timestamp: new Date().toISOString()
        });
      }
    } catch (error) {
      console.error('Chatbot error:', error);
      setMessages(prev => [...prev, { 
        sender: 'bot', 
        text: 'Sorry, I encountered an error. Please try again.' 
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="chatbot-interface">
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
        {isTyping && (
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}
      </div>
      <div className="chat-input">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type your message..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default ChatbotInterface;