# Hotel AI System with FastAPI and Flask

This project implements a hotel AI system with a chatbot interface that connects to AI agents for handling various guest requests. The system uses FastAPI for WebSocket communication and separate Flask applications for each frontend page.

## Features

- Guest chatbot interface for making requests
- Room service dashboard for handling food and drink orders
- Admin dashboard for maintenance requests and bookings
- AI agents that process guest requests and send notifications to the appropriate dashboards
- Real-time updates using WebSockets

## Architecture

- **Backend**:
  - FastAPI server for WebSocket communication and API endpoints
  - Python-based AI agents for processing guest requests

- **Frontend**:
  - Three separate Flask applications:
    - Guest App: For guests to interact with the chatbot
    - Admin App: For admin notifications (maintenance, bookings)
    - Room Service App: For room service team notifications (food, drinks)
  - Each app has its own HTML/CSS/JavaScript interface
  - WebSocket connections for real-time updates

## Setup and Installation

### Using Docker (Recommended)

1. Make sure you have Docker and Docker Compose installed on your system.

2. Clone the repository:
   ```
   git clone <repository-url>
   cd project-HAI
   ```

3. Build and start the containers:
   ```
   docker-compose up --build
   ```

4. Access the applications:
   - Guest Chatbot: http://localhost:5001/
   - Admin Dashboard: http://localhost:5002/
   - Room Service Dashboard: http://localhost:5003/

### Manual Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd project-HAI
   ```

2. Install backend dependencies:
   ```
   cd backend
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```
   pip install flask flask-cors requests
   ```

4. Start the backend server:
   ```
   cd backend
   uvicorn fastapi_server:app --host 0.0.0.0 --port 8000
   ```

5. Start the frontend applications (in separate terminals):
   ```
   # Guest App
   cd frontend/guest-app
   flask run --host=0.0.0.0 --port=5001

   # Admin App
   cd frontend/admin-app
   flask run --host=0.0.0.0 --port=5002

   # Room Service App
   cd frontend/room-service-app
   flask run --host=0.0.0.0 --port=5003
   ```

6. Access the applications:
   - Guest Chatbot: http://localhost:5001/
   - Admin Dashboard: http://localhost:5002/
   - Room Service Dashboard: http://localhost:5003/

## Testing the System

1. Open the Guest Chatbot page and enter your room number (e.g., 101).
2. Send a message like "I'd like to order a burger and fries" - this should trigger the Room Service Agent.
3. Check the Room Service Dashboard to see the notification for the food order.
4. Go back to the Guest Chatbot and send a message like "The sink in my bathroom is leaking" - this should trigger the Maintenance Agent.
5. Check the Admin Dashboard to see the notification for the maintenance request.

## Docker Container Structure

- **backend**: Contains the FastAPI server and AI agents
- **guest-app**: Contains the Flask application for the guest chatbot
- **admin-app**: Contains the Flask application for the admin dashboard
- **room-service-app**: Contains the Flask application for the room service dashboard

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
2. Frontend: Edit templates in the respective app's `templates` directory
3. Backend: Edit `fastapi_server.py` as needed

## Troubleshooting

- If the WebSocket connection fails, check that the backend server is running
- If agents aren't responding, check the console logs for errors
- Make sure all dependencies are installed correctly
- If using Docker, check the container logs for any errors:
  ```
  docker-compose logs backend
  docker-compose logs guest-app
  docker-compose logs admin-app
  docker-compose logs room-service-app