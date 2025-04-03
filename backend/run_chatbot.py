import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from chatbot_app import ChatbotApp

def main():
    print("Starting Separate Guest Chatbot on port 5001...")
    chatbot_app = ChatbotApp()
    chatbot_app.run(port=5001)

if __name__ == '__main__':
    main()