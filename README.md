# Hotel Management System

A comprehensive web application for hotel management with real-time features.

## Features

1. **Backend Alert System**: Real-time alert counter that increments each time an ALERT button is pressed.
2. **Database Integration**: Connects to SQLite database (hotel_bookings.db) to display booking information categorized as "upcoming," "current," and "past."
3. **Laundry Alert Notification System**: Allows backend users to specify room numbers to send targeted alerts.
4. **AI Chatbot Assistant**: Interactive chatbot that assists hotel guests with inquiries and requests.
   - Uses locally downloaded GPT-2 model for offline operation
   - Optional Hugging Face API integration
   - Customizable system prompt for hotel-specific responses

## Project Structure

The project follows a modern full-stack architecture:

- **Frontend**: React.js application with Material-UI components
- **Backend**: Node.js with Express.js
- **Database**: SQLite (hotel_bookings.db)
- **Real-time Communication**: Socket.IO

## Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)

## Quick Start Guide

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd hotel-management-system
   ```

2. **One-command setup and run**:
   ```
   npm run setup-and-start
   ```
   This will install all dependencies and start the application.

## Manual Installation

1. **Install root dependencies**:
   ```
   npm install
   ```

2. **Install backend and frontend dependencies**:
   ```
   npm run install:all
   ```

3. **Start the application**:
   ```
   npm start
   ```

## Environment Variables

All environment variables are included in the repository for easy setup:

- Backend environment variables are in `backend/.env`
- Default port for backend: 5000
- Default port for frontend: 3000

## Database Setup

The SQLite database file (hotel_bookings.db) is included in the repository. No additional setup is required.

If you want to reset the database, simply delete the file and restart the application. The tables will be automatically recreated.

## Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000/api

## Development

### Running Components Separately

```
# Start backend only
npm run start:backend

# Start frontend only
npm run start:frontend
```

### Project Structure

```
project-root/
├── frontend/                  # React frontend application
│   ├── public/                # Static files
│   └── src/                   # Source code
│       ├── components/        # UI components
│       │   ├── alerts/        # Alert system components
│       │   ├── bookings/      # Booking management components
│       │   ├── chatbot/       # AI chatbot components
│       │   ├── common/        # Shared UI components
│       │   └── notifications/ # Notification system components
│       ├── contexts/          # State management
│       ├── pages/             # Page components
│       └── services/          # API and WebSocket services
│
├── backend/                   # Node.js backend application
│   ├── config/                # Configuration files
│   ├── controllers/           # Request handlers
│   ├── models/                # Database models
│   ├── routes/                # API routes
│   ├── services/              # Business logic
│   ├── chatbot_bridge.py      # Python bridge for Hugging Face API
│   ├── local_model_chatbot.py # Python script for local GPT-2 model
│   └── models/                # Directory for downloaded AI models
│
├── hotel_bookings.db          # SQLite database file
├── setup_chatbot.py           # Setup script for chatbot feature
├── test_gpu_and_model.py      # Test script for GPU and model
├── CHATBOT_SETUP.md           # Chatbot setup instructions
└── LOCAL_MODEL_README.md      # Detailed local model documentation
```

## API Endpoints

### Bookings API
- `GET /api/bookings` - Get all bookings
- `GET /api/bookings/upcoming` - Get upcoming bookings
- `GET /api/bookings/current` - Get current bookings
- `GET /api/bookings/past` - Get past bookings
- `GET /api/bookings/:id` - Get booking by ID

### Alerts API
- `GET /api/alerts` - Get alert history
- `GET /api/alerts/count` - Get current alert count
- `POST /api/alerts` - Create a new alert
- `PUT /api/alerts/:id/resolve` - Resolve an alert
- `POST /api/alerts/reset` - Reset alert counter

### Notifications API
- `GET /api/notifications` - Get all notifications
- `POST /api/notifications` - Create a new notification
- `GET /api/notifications/room/:roomNumber` - Get notifications for a specific room
- `PUT /api/notifications/:id/read` - Mark a notification as read
- `POST /api/notifications/laundry` - Send a laundry alert notification

## WebSocket Events

### Server to Client Events
- `alert_count_updated` - Broadcast updated alert count
- `new_booking` - Broadcast when a new booking is added
- `booking_updated` - Broadcast when a booking is updated
- `new_notification` - Send targeted notification

### Client to Server Events
- `trigger_alert` - Client triggers an alert
- `send_notification` - Send a notification to specific room(s)
- `join_room` - Join a specific notification room

## Troubleshooting

### Common Issues

1. **Port conflicts**: If ports 3000 or 5000 are already in use, you can modify the port in:
   - Backend: Edit `PORT` in `backend/.env`
   - Frontend: Create a `.env` file in the frontend directory with `PORT=3001`

2. **Database errors**: If you encounter database errors, try deleting the `hotel_bookings.db` file and restart the application.

3. **Missing dependencies**: If you encounter errors about missing modules, run:
   ```
   npm run install:all
   ```

## License

This project is licensed under the ISC License.