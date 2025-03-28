import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
import os
import logging
import requests
import json
from flask_cors import CORS
from flask_socketio import SocketIO
import socketio as python_socketio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("guest_app")

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',
    logger=True,
    engineio_logger=True
)

# Create Socket.IO client for backend connection
backend_socket = None

# Configuration
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5002")

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    global backend_socket
    try:
        # Connect to backend Socket.IO server
        if not backend_socket:
            backend_socket = python_socketio.Client(logger=True, engineio_logger=True)
            
            @backend_socket.on('message')
            def on_backend_message(data):
                # Forward backend messages to frontend
                socketio.emit('message', data)
            
            backend_socket.connect(BACKEND_URL, wait_timeout=5)
            
        logger.info("Client connected")
        socketio.emit('message', {'response': 'Connected to server'})
    except Exception as e:
        logger.error(f"Error connecting to backend: {e}")
        socketio.emit('message', {'response': 'Error connecting to backend server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    global backend_socket
    try:
        if backend_socket:
            backend_socket.disconnect()
            backend_socket = None
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting from backend: {e}")

@socketio.on('message')
def handle_message(data):
    """Handle messages from frontend and proxy to backend"""
    global backend_socket
    try:
        logger.info(f"Received message from frontend: {data}")
        
        if isinstance(data, str):
            data = json.loads(data)
            logger.info("Parsed string data to JSON")
            
        if backend_socket and backend_socket.connected:
            # Forward message to backend
            logger.info(f"Forwarding message to backend: {data}")
            backend_socket.emit('message', data)
            logger.info("Message forwarded successfully")
        else:
            logger.warning("Backend socket not connected, attempting reconnection...")
            # Try to reconnect to backend
            try:
                if not backend_socket:
                    logger.info("Creating new backend socket connection...")
                    backend_socket = python_socketio.Client(logger=True, engineio_logger=True)
                    
                    @backend_socket.on('message')
                    def on_backend_message(msg_data):
                        # Forward backend messages to frontend
                        logger.info(f"Received message from backend: {msg_data}")
                        socketio.emit('message', msg_data)
                        logger.info("Forwarded backend message to frontend")
                    
                    logger.info(f"Connecting to backend at {BACKEND_URL}...")
                    backend_socket.connect(BACKEND_URL, wait_timeout=5)
                    logger.info("Backend connection established")
                    
                    # Retry sending message after reconnection
                    logger.info("Retrying message after reconnection...")
                    backend_socket.emit('message', data)
                    logger.info("Message resent successfully")
                else:
                    logger.error("Backend connection not available")
                    socketio.emit('message', {'response': 'Backend server not available'})
            except Exception as conn_err:
                logger.error(f"Error reconnecting to backend: {conn_err}", exc_info=True)
                socketio.emit('message', {'response': 'Error connecting to backend server'})
    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)
        socketio.emit('message', {'response': 'Error processing your request'})

@app.route('/')
def index():
    """Serve the guest chatbot page"""
    return render_template('index.html', backend_url=BACKEND_URL)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check if backend server is running
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            return jsonify({
                "status": "ok",
                "guest_app": "running",
                "backend_server": "running"
            })
        else:
            return jsonify({
                "status": "warning",
                "guest_app": "running",
                "backend_server": "not responding properly"
            })
    except requests.RequestException:
        return jsonify({
            "status": "warning",
            "guest_app": "running",
            "backend_server": "not reachable"
        })

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 5001))
    socketio.run(app, host='localhost', port=port, debug=True, allow_unsafe_werkzeug=True)