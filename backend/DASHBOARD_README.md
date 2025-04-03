# Hotel AI Dashboard Access

## Running the Application

1. Ensure you have all dependencies installed:
   ```
   pip install -r requirements.txt
   ```

2. Start the Flask application:
   ```
   python flask_app.py
   ```

## Dashboard URLs

### 1. Room Service Dashboard
- **URL**: `http://localhost:5000/room-service`
- **Features**:
  - Real-time housekeeping requests
  - Current room service orders
  - Instant notifications

### 2. Admin Dashboard
- **URL**: `http://localhost:5000/admin`
- **Features**:
  - Guest request tracking
  - System-wide notifications
  - Comprehensive request overview

## WebSocket Connectivity

Both dashboards use WebSocket connections to receive real-time updates:
- Room Service Dashboard connects to `/room-service` namespace
- Admin Dashboard connects to `/admin` namespace

## Testing Dashboard Functionality

Try these example queries to see dashboard updates:
1. "I need towels in room 102"
2. "I want to order a burger and fries for room 202"

Queries will trigger corresponding dashboard notifications in real-time.