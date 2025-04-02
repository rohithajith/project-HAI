# Hotel AI System with Local LLM and Flask

This project implements a hotel AI system with a chatbot interface that connects to AI agents for handling various guest requests. The system uses Flask with Socket.IO for real-time communication and local LLM integration for processing requests.

## Features

- Guest chatbot interface for making requests
- Room service dashboard for handling food and drink orders
- Admin dashboard for maintenance requests and bookings
- AI agents that process guest requests using local LLM
- Real-time updates using Socket.IO
- Local model processing without external API calls

## Architecture

- **Backend**:
  - Flask server with Socket.IO for real-time communication
  - Python-based AI agents using local LLM for processing guest requests
  - LangGraph for agent orchestration
  - Pydantic for schema validation

- **Frontend**:
  - Unified Flask application serving three interfaces:
    - Guest Chatbot: For guests to interact with the AI
    - Admin Dashboard: For admin notifications
    - Room Service Dashboard: For room service team notifications
  - Real-time WebSocket communication using Socket.IO
  - Responsive UI with status management

## Recent Changes

### Frontend Changes
- `backend/templates/base.html`: Updated base template with unified styling
- `backend/templates/index.html`: Enhanced guest chatbot with room validation
- `backend/templates/admin.html`: Added real-time notification system
- `backend/templates/room_service.html`: Added request management system

### Backend Changes
- `backend/flask_app.py`: 
  - Implemented Socket.IO namespaces for different interfaces
  - Added proper error handling
  - Integrated with agent manager for local LLM processing

### Agent System Changes
- `backend/ai_agents/agent_manager_corrected.py`: Enhanced for local model usage
- `backend/ai_agents/supervisor_agent.py`: Added LangGraph workflow support

## Setup and Installation

1. Ensure you have the local model in `finetunedmodel-merged` directory
2. Install requirements: `pip install -r requirements.txt`
3. Run the Flask server: `python backend/flask_app.py`
4. Access the interfaces:
   - Guest Chatbot: http://localhost:5000/
   - Admin Dashboard: http://localhost:5000/admin
   - Room Service Dashboard: http://localhost:5000/room-service

## Testing the System Flow

1. Open the Guest Chatbot page and enter your room number (e.g., 101)
2. Send a message like "I need extra towels" or "Can I order room service?"
3. The request will be processed by the local LLM through the agent system
4. Check the appropriate dashboard (Room Service or Admin) to see the notification
5. Use the dashboard controls to manage request status (Start Preparing, Mark Delivered)

## WebSocket Namespaces

- `/guest`: For guest chatbot communication
- `/admin`: For admin dashboard notifications
- `/room-service`: For room service dashboard notifications

## Development

To modify or extend the system:

1. AI Agents: Edit files in the `backend/ai_agents` directory
2. Frontend: Edit templates in `backend/templates` directory
3. Backend: Edit `backend/flask_app.py` as needed

## Troubleshooting

- If the Socket.IO connection fails, check that the Flask server is running
- If agents aren't responding, check that the local model is properly loaded
- Make sure all dependencies are installed correctly
- Check the console logs for detailed error messages
- Verify the local model path in `agent_manager_corrected.py`

## Local Model Integration

The system uses a local LLM model for processing requests:
- Model Location: `finetunedmodel-merged`
- Loading: Handled by `local_model_chatbot.py`
- Features:
  - 8-bit quantization
  - Automatic device mapping
  - Thread-safe loading
  - Caching mechanism