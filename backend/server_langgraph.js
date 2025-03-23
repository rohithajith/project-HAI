
const app = require('./app_langgraph');
const http = require('http');
const socketIo = require('socket.io');
const socketService = require('./services/socketService');

// Set port
const port = process.env.PORT || 5001;

// Create HTTP server
const server = http.createServer(app);

// Initialize Socket.IO
const io = socketIo(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

// Initialize socket service
socketService.init(io);

// Start server
server.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
  