# Real-Time Agent Update WebSocket Integration

## Overview
This project implements a real-time WebSocket communication system between backend agents and frontend dashboards.

## Components

### Backend (WebSocket Server)
- Location: `backend/websocket_server.py`
- Responsibilities:
  - Watch `agent_logs` directory for new log files
  - Emit real-time updates to connected frontend clients
  - Provide a centralized communication hub for agent interactions

### Frontend WebSocket Service
- Location: `frontend/src/services/websocket-service.js`
- Responsibilities:
  - Establish WebSocket connection with backend
  - Route updates to specific dashboard components
  - Manage WebSocket connection lifecycle

### Dashboard Components
1. Room Service Dashboard (`RoomServiceDashboard.js`)
   - Handles room service specific updates
   - Displays:
     - Notifications
     - Current Orders
     - Housekeeping Requests

2. Admin Dashboard (`AdminDashboard.js`)
   - Tracks all agent interactions
   - Displays:
     - Detailed agent interaction logs
     - System-wide notifications

## Update Flow
1. Agent generates a log file in `agent_logs`
2. WebSocket server detects new log file
3. Server emits update to connected clients
4. Frontend WebSocket service routes update to appropriate dashboard
5. Dashboard updates its state and re-renders

## Configuration
- WebSocket Server: `http://localhost:5001`
- Supported Dashboard Components:
  - `room_service_dashboard`
  - `admin_dashboard`

## Example Agent Update JSON
```json
{
  "component": "room_service_dashboard",
  "action": "show_notification",
  "message": "Fresh towels are being prepared for your room",
  "details": {
    "agent": "room_service_agent",
    "timestamp": "2025-04-03T12:33:25.287682+00:00"
  }
}
```

## Dependencies
- Backend: Flask-SocketIO
- Frontend: socket.io-client
- File Watching: watchdog