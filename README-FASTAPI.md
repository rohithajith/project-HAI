# Hotel AI System with FastAPI and Flask

This project implements a hotel AI system with a chatbot interface that connects to AI agents for handling various guest requests. The system uses FastAPI for WebSocket communication and Flask for serving the frontend.

## Features

- Guest chatbot interface for making requests
- Room service dashboard for handling food and drink orders
- Admin dashboard for maintenance requests and bookings
- AI agents that process guest requests and send notifications to the appropriate dashboards
- Real-time updates using WebSockets

## Architecture

- **Backend**:
  - FastAPI server for WebSocket communication and API endpoints
  - Flask server for serving the frontend
  - Python-based AI agents for processing guest requests
  - Both servers run concurrently using threading

- **Frontend**:
  - Simple HTML/CSS/JavaScript interface
  - WebSocket connections for real-time updates
  - Separate pages for guest, room service, and admin

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. Clone the repository:
   ```
   git clone <repository-url>
   cd project-HAI
   ```

2. Install Python dependencies:
   ```
   pip install -r backend/requirements.txt
   ```

## Running the Application

1. Start the backend servers:
   ```
   cd backend
   python main.py
   ```

   This will start both the FastAPI server (on port 8000) and the Flask server (on port 5000).

2. Access the application:
   - Guest Chatbot: http://localhost:5000/
   - Admin Dashboard: http://localhost:5000/admin
   - Room Service Dashboard: http://localhost:5000/room-service

## Testing the System

1. Open the Guest Chatbot page and enter your room number.
2. Send a message like "I'd like to order a burger and fries" or "The sink in my bathroom is leaking".
3. The AI agents will process your request and send a response.
4. Check the Room Service Dashboard or Admin Dashboard to see the notifications.

## AI Agents

The system includes the following AI agents:

- **Room Service Agent**: Handles food and drink orders
- **Maintenance Agent**: Handles maintenance requests and scheduling

Each agent has specific tools and capabilities for processing different types of requests.

## WebSocket Endpoints

- `/ws/guest`: For guest chatbot communication
- `/ws/admin`: For admin dashboard notifications
- `/ws/room-service`: For room service dashboard notifications

## HTTP Endpoints

- `/api/message`: For sending messages via HTTP (alternative to WebSocket)
- `/health`: For checking the health of the system
- `/`: Root endpoint

## Development

To modify or extend the system:

1. AI Agents: Edit files in the `backend/ai_agents` directory
2. Frontend: Edit templates in the `backend/templates` directory
3. Backend: Edit `fastapi_server.py` or `flask_app.py` as needed

## Troubleshooting

- If the WebSocket connection fails, check that both servers are running
- If agents aren't responding, check the console logs for errors
- Make sure all dependencies are installed correctly