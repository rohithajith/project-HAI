import os
import sys
import json
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import the agent manager
from backend.ai_agents.agent_manager_corrected import agent_manager_corrected

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ChatbotApp:
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.app = Flask(__name__, template_folder=template_dir)
        CORS(self.app)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('chatbot.html')

        @self.app.route('/send_message', methods=['POST'])
        def send_message():
            try:
                data = request.json
                message = data.get('message', '')
                room_number = data.get('room_number', '101')

                logger.debug(f"Received message: {message}")

                try:
                    # Process message through agent manager
                    response = agent_manager_corrected.process(message, [])
                    logger.debug(f"Agent response: {response}")

                    return jsonify({
                        'status': 'success',
                        'response': response.response
                    })
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    return jsonify({
                        'status': 'error',
                        'message': str(e)
                    }), 500

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return jsonify({
                    'status': 'error',
                    'message': 'Internal server error'
                }), 500

    def run(self, debug=True, port=5001):
        """Run the Flask application."""
        self.app.run(host='0.0.0.0', port=port, debug=debug)

def main():
    chatbot_app = ChatbotApp()
    chatbot_app.run()

if __name__ == '__main__':
    main()