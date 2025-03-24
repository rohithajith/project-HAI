const express = require('express');
const cors = require('cors');
const path = require('path');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// Import routes
const authRoutes = require('./routes/authRoutes');
const userRoutes = require('./routes/userRoutes');
const bookingRoutes = require('./routes/bookingRoutes');
const alertRoutes = require('./routes/alertRoutes');
const notificationRoutes = require('./routes/notificationRoutes');
const chatbotRoutes = require('./routes/chatbotRoutes');
const chatbotLangGraphRoutes = require('./routes/chatbotRoutes_langgraph');
const hotelInfoRoutes = require('./routes/hotelInfoRoutes');

// Initialize express app
const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// API routes
app.use('/api/auth', authRoutes);
app.use('/api/users', userRoutes);
app.use('/api/bookings', bookingRoutes);
app.use('/api/alerts', alertRoutes);
app.use('/api/notifications', notificationRoutes);
app.use('/api/hotel-info', hotelInfoRoutes);

// Choose which chatbot implementation to use based on environment variable
if (process.env.USE_LANGGRAPH_CHATBOT === 'true') {
  console.log('Using LangGraph multi-agent chatbot');
  app.use('/api/chatbot', chatbotLangGraphRoutes);
} else {
  console.log('Using legacy chatbot');
  app.use('/api/chatbot', chatbotRoutes);
}

// Add a route to check if the LangGraph API is available
app.get('/api/chatbot-status', async (req, res) => {
  try {
    if (process.env.USE_LANGGRAPH_CHATBOT !== 'true') {
      return res.json({ 
        status: 'legacy',
        message: 'Using legacy chatbot. Set USE_LANGGRAPH_CHATBOT=true to use LangGraph.'
      });
    }
    
    const chatbotController = require('./controllers/chatbotController_langgraph');
    const healthCheckResult = await chatbotController.healthCheck(req, res);
    
    // If healthCheck doesn't send a response, we'll send one here
    if (!res.headersSent) {
      return res.json({ 
        status: 'langgraph',
        message: 'LangGraph chatbot is active and healthy.'
      });
    }
  } catch (error) {
    console.error('Error checking chatbot status:', error);
    return res.status(500).json({ 
      status: 'error',
      message: 'Error checking chatbot status'
    });
  }
});

// Serve static files in production
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, '../frontend/build')));
  
  app.get('*', (req, res) => {
    res.sendFile(path.resolve(__dirname, '../frontend', 'build', 'index.html'));
  });
}

// Error handling middleware
app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  res.status(statusCode).json({
    status: 'error',
    statusCode,
    message: err.message,
    stack: process.env.NODE_ENV === 'production' ? '🥞' : err.stack
  });
});

module.exports = app;