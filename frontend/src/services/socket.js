import { io } from 'socket.io-client';

const SOCKET_URL = 'http://localhost:5000';

class SocketService {
  constructor() {
    this.socket = null;
    this.listeners = {};
  }

  // Connect to WebSocket server
  connect() {
    if (this.socket) return;

    this.socket = io(SOCKET_URL);
    
    this.socket.on('connect', () => {
      console.log('Connected to WebSocket server');
    });
    
    this.socket.on('disconnect', () => {
      console.log('Disconnected from WebSocket server');
    });
    
    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
    
    // Set up listeners that were registered before connection
    Object.entries(this.listeners).forEach(([event, callbacks]) => {
      callbacks.forEach(callback => {
        this.socket.on(event, callback);
      });
    });
  }

  // Disconnect from WebSocket server
  disconnect() {
    if (!this.socket) return;
    
    this.socket.disconnect();
    this.socket = null;
  }

  // Add event listener
  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    
    this.listeners[event].push(callback);
    
    if (this.socket) {
      this.socket.on(event, callback);
    }
  }

  // Remove event listener
  off(event, callback) {
    if (!this.listeners[event]) return;
    
    this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    
    if (this.socket) {
      this.socket.off(event, callback);
    }
  }

  // Emit event
  emit(event, data) {
    if (!this.socket) {
      console.warn('Socket not connected. Attempting to connect...');
      this.connect();
    }
    
    this.socket.emit(event, data);
  }

  // Join a room
  joinRoom(roomNumber) {
    this.emit('join_room', roomNumber);
  }

  // Trigger an alert
  triggerAlert() {
    this.emit('trigger_alert');
  }

  // Send a notification to a specific room
  sendNotification(roomNumber, message) {
    this.emit('send_notification', { roomNumber, message });
  }
}

// Create singleton instance
const socketService = new SocketService();

export default socketService;