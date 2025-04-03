# Hotel AI Chatbot Application

## Overview
This is a separate web application for the hotel AI chatbot, running on a different port and providing real-time communication and monitoring capabilities.

## Features
- Standalone chatbot interface
- Real-time message broadcasting to Admin and Room Service dashboards
- Integrated with multi-agent AI system
- Separate port from main application

## Prerequisites
- Python 3.8+
- Virtual environment recommended
- Install dependencies from `requirements.txt`

## Setup and Installation

1. Create a virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

### Start the Chatbot Application
```bash
python run_chatbot.py
```

The application will start on `http://localhost:5001`

## Accessing Dashboards

1. Guest Chatbot: `http://localhost:5001/`
2. Admin Dashboard: `http://localhost:5001/admin`
3. Room Service Dashboard: `http://localhost:5001/room-service`

## Debugging
- Check `chatbot_debug.log` for detailed logs
- Logging is configured to output to both console and file

## Key Components
- `chatbot_app.py`: Main Flask application
- `templates/chatbot.html`: Guest chatbot interface
- `templates/admin.html`: Admin monitoring dashboard
- `templates/room_service.html`: Room service monitoring dashboard

## Troubleshooting
- Ensure all dependencies are installed
- Check that the AI agent system is properly configured
- Verify network ports are available

## Notes
- The application uses Server-Sent Events (SSE) for real-time updates
- Messages are processed through the multi-agent AI system
- Dashboards update in real-time when messages are sent