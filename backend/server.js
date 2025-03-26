const app = require('./app');
const http = require('http');
const socketService = require('./services/socketService');
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables
dotenv.config();

// Set port
const port = process.env.PORT || 5000;
app.set('port', port);

// Create HTTP server
const server = http.createServer(app);

// Initialize socket.io
socketService.init(server);

// Serve static files in production
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, '../frontend/build')));

  app.get('*', (req, res) => {
    res.sendFile(path.resolve(__dirname, '../frontend', 'build', 'index.html'));
  });
}

// Start server
server.listen(port, () => {
  console.log(`Server running on port ${port}`);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (err) => {
  console.log('UNHANDLED REJECTION! 💥 Shutting down...');
  console.log(err.name, err.message);
  server.close(() => {
    process.exit(1);
  });
});