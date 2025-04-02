import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit, Namespace
import os
import sys
import json
import logging
import time
import asyncio
from ai_agents.room_service_agent import RoomServiceAgent

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("simple_flask_app")

# Also enable debug logging for socketio and engineio
logging.getLogger('socketio').setLevel(logging.DEBUG)
logging.getLogger('engineio').setLevel(logging.DEBUG)

# Create Flask app and SocketIO instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',
    async_handlers=True,
    logger=True,
    engineio_logger=True
)

# Initialize room service agent directly
room_service_agent = RoomServiceAgent()

# WebSocket namespaces
class GuestNamespace(Namespace):
    def on_connect(self):
        logger.info("Guest client connected")
        emit('message', {'response': 'Connected to server'})

    def on_disconnect(self):
        logger.info("Guest client disconnected")

    def on_message(self, data):
        try:
            if isinstance(data, str):
                data = json.loads(data)
            
            message = data.get('message', '')
            history = data.get('history', [])
            room = data.get('room', '')
            
            logger.info(f"Received message from room {room}: '{message}'")
            
            # Check if it's a towel request
            if 'towel' in message.lower():
                # Process with room service agent
                try:
                    # Get response from room service agent
                    response_coro = room_service_agent.process(message, history)
                    
                    # Run the coroutine in an event loop
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        response = loop.run_until_complete(response_coro)
                    finally:
                        loop.close()
                    
                    # Send response to guest
                    emit('message', {
                        'response': response.response,
                        'notifications': response.notifications
                    })
                    
                    # Broadcast to room service dashboard
                    socketio.emit('notification', {
                        'event': 'room_service_request',
                        'payload': {
                            'roomNumber': room,
                            'request': message,
                            'timestamp': time.time()
                        }
                    }, namespace='/room-service')
                    
                    # Also notify admin dashboard
                    socketio.emit('notification', {
                        'event': 'room_service_request',
                        'payload': {
                            'roomNumber': room,
                            'request': message,
                            'timestamp': time.time()
                        }
                    }, namespace='/admin')
                    
                except Exception as e:
                    logger.error(f"Error processing with agent: {e}", exc_info=True)
                    emit('message', {
                        'response': f"I apologize, but I encountered an error processing your request: {str(e)}",
                        'notifications': []
                    })
            else:
                # Generic response for other messages
                emit('message', {
                    'response': f"I understand you're in room {room}. How else can I assist you today?"
                })
            
        except Exception as e:
            logger.error(f"Error in message handler: {e}", exc_info=True)
            emit('message', {'response': "An error occurred while processing your request."})

class AdminNamespace(Namespace):
    def on_connect(self):
        logger.info("Admin client connected")
        emit('connection_status', {'status': 'connected'})

    def on_disconnect(self):
        logger.info("Admin client disconnected")

class RoomServiceNamespace(Namespace):
    def on_connect(self):
        logger.info("Room service client connected")
        emit('connection_status', {'status': 'connected'})

    def on_disconnect(self):
        logger.info("Room service client disconnected")

# Register namespaces
socketio.on_namespace(GuestNamespace('/guest'))
socketio.on_namespace(AdminNamespace('/admin'))
socketio.on_namespace(RoomServiceNamespace('/room-service'))

@app.route('/')
def index():
    """Serve the guest chatbot page"""
    return render_template('index.html')

@app.route('/admin')
def admin():
    """Serve the admin dashboard page"""
    return render_template('admin.html')

@app.route('/room-service')
def room_service():
    """Serve the room service dashboard page"""
    return render_template('room_service.html')

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=5000, debug=True)