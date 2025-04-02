import unittest
import socketio
import time
import json
from flask import Flask
from flask_socketio import SocketIO
from ai_agents.agent_manager import AgentManagerCorrected
from flask_app import app, socketio as server_socketio
from local_model_chatbot import load_model_and_tokenizer
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestAgentSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Load the model once for all tests"""
        logger.info("Loading local model for testing...")
        cls.model, cls.tokenizer, cls.device = load_model_and_tokenizer()
        if not all([cls.model, cls.tokenizer, cls.device]):
            raise Exception("Failed to load local model and tokenizer")
        logger.info("Local model loaded successfully")

    def setUp(self):
        # Set up test client
        self.app = app
        self.client = self.app.test_client()
        
        # Set up SocketIO test client
        self.socketio_client = socketio.Client()
        
        # Store received messages
        self.received_messages = []
        
        # Initialize agent manager with local model
        self.agent_manager = AgentManagerCorrected()
        
        # Connect to server
        try:
            self.socketio_client.connect('http://localhost:5002')
            logger.info("Connected to WebSocket server")
        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            raise
            
    def tearDown(self):
        # Disconnect socket client
        if self.socketio_client.connected:
            self.socketio_client.disconnect()
            logger.info("Disconnected from WebSocket server")
            
    def test_room_service_request(self):
        """Test the room service request flow with all agents"""
        logger.info("\nTesting room service request flow...")
        
        # Set up message handler
        @self.socketio_client.on('message')
        def handle_message(data):
            logger.info(f"Received response: {data}")
            self.received_messages.append(data)
        
        # Test message for towel request
        test_message = "hi, can i get towels"
        logger.info(f"\nSending test message: {test_message}")
        
        # Emit test message
        self.socketio_client.emit('message', {
            'message': test_message,
            'history': []
        })
        
        # Wait for response (max 10 seconds)
        timeout = 10
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.received_messages:
                break
            time.sleep(0.1)
            
        # Assert we got a response
        self.assertTrue(len(self.received_messages) > 0, "No response received from server")
        
        # Check response content
        response = self.received_messages[0]
        self.assertIn('response', response, "Response missing 'response' field")
        
        # Log response for verification
        logger.info(f"\nResponse received: {response['response']}")
        
        # Check for notifications if any
        if 'notifications' in response:
            logger.info(f"Notifications: {response['notifications']}")
            
        # Verify room service agent processed request
        self.assertNotIn("Echo:", response['response'], 
                        "Response appears to be echo mode, agents may not be working")
        
        # Verify response mentions towels
        self.assertIn("towel", response['response'].lower(), 
                     "Response should acknowledge towel request")

def run_tests():
    logger.info("Starting agent system tests...")
    unittest.main(argv=[''], verbosity=2)

if __name__ == '__main__':
    run_tests()