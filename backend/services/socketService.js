const socketIO = require('socket.io');

let io;
let alertCount = 0; // In-memory alert counter

/**
 * Initialize Socket.IO server
 * @param {Object} server - HTTP server instance
 */
function init(server) {
  io = socketIO(server, {
    cors: {
      origin: '*',
      methods: ['GET', 'POST']
    }
  });

  io.on('connection', (socket) => {
    console.log('New client connected:', socket.id);
    
    // Send current alert count to newly connected client
    socket.emit('alert_count_updated', alertCount);
    
    // Handle alert trigger
    socket.on('trigger_alert', () => {
      alertCount++;
      console.log('Alert triggered. New count:', alertCount);
      
      // Broadcast updated count to all clients
      io.emit('alert_count_updated', alertCount);
    });
    
    // Handle room-specific notifications
    socket.on('send_notification', (data) => {
      if (!data.roomNumber || !data.message) {
        socket.emit('error', { message: 'Room number and message are required' });
        return;
      }
      
      console.log(`Notification for room ${data.roomNumber}: ${data.message}`);
      
      // Broadcast notification to specific room
      io.emit('new_notification', {
        roomNumber: data.roomNumber,
        message: data.message,
        timestamp: new Date().toISOString()
      });
    });
    
    // Handle client joining a specific room
    socket.on('join_room', (roomNumber) => {
      socket.join(`room_${roomNumber}`);
      console.log(`Client ${socket.id} joined room_${roomNumber}`);
    });
    
    // Handle disconnection
    socket.on('disconnect', () => {
      console.log('Client disconnected:', socket.id);
    });
  });

  console.log('Socket.IO initialized');
  return io;
}

/**
 * Get Socket.IO instance
 * @returns {Object} Socket.IO instance
 */
function getIO() {
  if (!io) {
    throw new Error('Socket.IO not initialized');
  }
  return io;
}

/**
 * Get current alert count
 * @returns {number} Current alert count
 */
function getAlertCount() {
  return alertCount;
}

/**
 * Reset alert count
 */
function resetAlertCount() {
  alertCount = 0;
  if (io) {
    io.emit('alert_count_updated', alertCount);
  }
  return alertCount;
}

module.exports = {
  init,
  getIO,
  getAlertCount,
  resetAlertCount
};