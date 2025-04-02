import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
import os
import sys
import json
import logging
from local_model_chatbot import load_model_and_tokenizer
from ai_agents.agent_manager_corrected import AgentManagerCorrected

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("flask_app")

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

# Initialize agent manager with local model
try:
    agent_manager = AgentManagerCorrected()
    logger.info("Agent Manager initialized successfully with local model")
except Exception as e:
    logger.error(f"Failed to initialize Agent Manager: {e}")
    agent_manager = None

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

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("Client connected")
    emit('message', {'response': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected")

@socketio.on('message')
def handle_message(data):
    """Handle incoming messages using eventlet for async operations"""
    try:
        logger.debug(f"Message handler received data: {data}")
        
        if isinstance(data, str):
            data = json.loads(data)
            logger.debug("Parsed string data to JSON")
        
        message = data.get('message', '')
        history = data.get('history', [])
        
        logger.info(f"Received message: '{message}'")
        logger.debug(f"Message history length: {len(history)}")
        
        # Spawn a greenthread to handle the message processing
        logger.debug("Spawning greenthread for message processing...")
        gt = eventlet.spawn(process_message, message, history)
        logger.debug("Greenthread spawned successfully")
        
        # Add callback to log when greenthread completes
        gt.link(lambda _: logger.debug("Message processing greenthread completed"))
        
    except Exception as e:
        logger.error(f"Error in message handler: {e}", exc_info=True)
        socketio.emit('message', {'response': "An error occurred while processing your request."})

def process_message(message, history):
    """Process message in a greenthread"""
    try:
        logger.debug(f"Starting process_message with message: '{message}'")
        logger.debug(f"Message history length: {len(history)}")
        
        if agent_manager:
            try:
                logger.info("Processing with agent manager...")
                result = agent_manager.process(message, history)
                if result and result.response:
                    logger.info(f"Agent manager generated response: {result.response}")
                    socketio.emit('message', {
                        'response': result.response,
                        'notifications': result.notifications if hasattr(result, 'notifications') else []
                    })
                    return
                else:
                    logger.warning("Agent manager returned no response")
            except Exception as e:
                logger.error(f"Error processing with agent: {e}", exc_info=True)
        
        # If we get here, agent manager didn't work
        logger.warning("No response generated, falling back to echo mode")
        socketio.emit('message', {'response': f"Echo: {message} (AI components not available)"})
            
    except Exception as e:
        logger.error(f"Error in process_message: {e}", exc_info=True)
        socketio.emit('message', {'response': "An error occurred while processing your request."})

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=5002, debug=True)