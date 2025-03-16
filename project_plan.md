# Comprehensive Web Application Plan

## 1. Architecture Overview

The application will follow a modern full-stack architecture with these key components:

```mermaid
graph TD
    subgraph "Frontend - React"
        A[React UI Components] --> B[State Management]
        B --> C[WebSocket Client]
        B --> D[HTTP Client/API Service]
    end
    
    subgraph "Backend - Node.js"
        E[Express Server] --> F[WebSocket Server]
        E --> G[API Routes]
        G --> H[Controllers]
        H --> I[Database Service]
        F --> J[Real-time Event Handler]
        J --> H
    end
    
    subgraph "Database"
        K[SQLite - hotel_bookings.db]
    end
    
    C <-->|Real-time Communication| F
    D <-->|HTTP Requests| G
    I <-->|CRUD Operations| K
```

## 2. Technology Stack

### Frontend
- **Framework**: React.js
- **State Management**: React Context API or Redux
- **WebSocket Client**: Socket.io-client
- **HTTP Client**: Axios
- **UI Framework**: Material-UI or Bootstrap
- **Build Tool**: Webpack (via Create React App)

### Backend
- **Runtime**: Node.js
- **Web Framework**: Express.js
- **WebSocket Server**: Socket.io
- **Database ORM**: Sequelize or better-sqlite3
- **Authentication**: JWT (if needed in the future)
- **Validation**: Joi or express-validator

### Database
- **SQLite**: Using the existing hotel_bookings.db file

## 3. Project Structure

```
project-root/
├── frontend/                  # React frontend application
│   ├── public/                # Static files
│   ├── src/
│   │   ├── assets/            # Images, fonts, etc.
│   │   ├── components/        # Reusable UI components
│   │   │   ├── alerts/        # Alert-related components
│   │   │   ├── bookings/      # Booking-related components
│   │   │   └── common/        # Common UI components
│   │   ├── contexts/          # React contexts for state management
│   │   ├── hooks/             # Custom React hooks
│   │   ├── pages/             # Page components
│   │   ├── services/          # API and WebSocket services
│   │   ├── utils/             # Utility functions
│   │   ├── App.js             # Main App component
│   │   └── index.js           # Entry point
│   ├── package.json
│   └── README.md
│
├── backend/                   # Node.js backend application
│   ├── config/                # Configuration files
│   ├── controllers/           # Request handlers
│   │   ├── alertController.js # Alert system controllers
│   │   ├── bookingController.js # Booking-related controllers
│   │   └── notificationController.js # Notification controllers
│   ├── models/                # Database models
│   ├── routes/                # API route definitions
│   ├── services/              # Business logic
│   │   ├── databaseService.js # Database interaction service
│   │   ├── socketService.js   # WebSocket service
│   │   └── notificationService.js # Notification handling
│   ├── utils/                 # Utility functions
│   ├── app.js                 # Express application setup
│   ├── server.js              # Server entry point
│   ├── package.json
│   └── README.md
│
├── .gitignore
├── package.json               # Root package.json for scripts
└── README.md                  # Project documentation
```

## 4. Feature Design

### 4.1 Backend Alert System

```mermaid
sequenceDiagram
    participant User as Frontend User
    participant FE as Frontend
    participant BE as Backend
    participant DB as Database
    
    User->>FE: Press ALERT button
    FE->>BE: Send alert event via WebSocket
    BE->>BE: Increment alert counter
    BE->>DB: Log alert event (optional)
    BE->>FE: Broadcast updated count to all clients
    FE->>User: Display updated count
```

**Implementation Details:**
- Create an alert counter stored in memory or database
- Implement WebSocket event handlers for alert events
- Broadcast counter updates to all connected clients
- Display real-time counter on frontend

### 4.2 Database Integration Module

```mermaid
graph TD
    A[Database Service] --> B[Query hotel_bookings.db]
    B --> C{Process Bookings}
    C --> D[Upcoming Bookings]
    C --> E[Current Bookings]
    C --> F[Past Bookings]
    D --> G[Frontend Display]
    E --> G
    F --> G
    G --> H[Filtering Options]
```

**Implementation Details:**
- Connect to SQLite database using appropriate Node.js library
- Create models for booking data
- Implement services to query and categorize bookings
- Add real-time updates for new bookings
- Create filtering options based on date, status, etc.
- Display bookings in organized UI components

### 4.3 Laundry Alert Notification System

```mermaid
sequenceDiagram
    participant Staff as Backend User
    participant BE as Backend
    participant WS as WebSocket Server
    participant FE as Frontend
    
    Staff->>BE: Enter room number & send alert
    BE->>BE: Create notification
    BE->>WS: Broadcast notification
    WS->>FE: Send targeted notification
    FE->>FE: Display notification in UI
```

**Implementation Details:**
- Create a notification form for backend users
- Implement room-specific targeting logic
- Store notifications in memory or database
- Broadcast notifications via WebSockets
- Display notifications in a dedicated UI area

## 5. Database Design (Assumptions)

Since we don't have the exact schema of hotel_bookings.db, we'll make assumptions and adjust during implementation:

```mermaid
erDiagram
    BOOKINGS {
        int id PK
        string guest_name
        string room_number
        datetime check_in
        datetime check_out
        string status
        datetime created_at
        datetime updated_at
    }
    
    ROOMS {
        string room_number PK
        string room_type
        string status
    }
    
    ALERTS {
        int id PK
        string type
        string message
        string room_number FK
        datetime created_at
        boolean is_resolved
    }
    
    ROOMS ||--o{ BOOKINGS : has
    ROOMS ||--o{ ALERTS : receives
```

## 6. API Endpoints

### Bookings API
- `GET /api/bookings` - Get all bookings
- `GET /api/bookings/upcoming` - Get upcoming bookings
- `GET /api/bookings/current` - Get current bookings
- `GET /api/bookings/past` - Get past bookings
- `GET /api/bookings/:id` - Get booking by ID
- `POST /api/bookings` - Create a new booking
- `PUT /api/bookings/:id` - Update a booking
- `DELETE /api/bookings/:id` - Delete a booking

### Alerts API
- `GET /api/alerts` - Get alert history
- `GET /api/alerts/count` - Get current alert count
- `POST /api/alerts` - Create a new alert
- `PUT /api/alerts/:id/resolve` - Resolve an alert

### Notifications API
- `GET /api/notifications` - Get all notifications
- `POST /api/notifications` - Create a new notification
- `GET /api/notifications/room/:roomNumber` - Get notifications for a specific room

## 7. WebSocket Events

### Server to Client Events
- `alert_count_updated` - Broadcast updated alert count
- `new_booking` - Broadcast when a new booking is added
- `booking_updated` - Broadcast when a booking is updated
- `new_notification` - Send targeted notification

### Client to Server Events
- `trigger_alert` - Client triggers an alert
- `send_notification` - Send a notification to specific room(s)
- `join_room` - Join a specific notification room

## 8. Implementation Plan

### Phase 1: Project Setup
1. Initialize project structure
2. Set up Express backend
3. Set up React frontend
4. Configure WebSocket connection
5. Connect to SQLite database

### Phase 2: Core Features
1. Implement database models and services
2. Create API endpoints
3. Implement alert counter system
4. Develop booking display and categorization
5. Create notification system

### Phase 3: Frontend Development
1. Build React components
2. Implement state management
3. Create UI for alerts, bookings, and notifications
4. Add filtering functionality
5. Implement real-time updates

### Phase 4: Testing & Refinement
1. Write unit tests
2. Perform integration testing
3. Optimize performance
4. Improve error handling
5. Refine UI/UX

### Phase 5: Deployment
1. Prepare for cloud hosting
2. Set up CI/CD pipeline
3. Configure production environment
4. Deploy application
5. Monitor performance

## 9. Testing Strategy

### Unit Testing
- Test individual components and functions
- Use Jest for JavaScript testing
- Test database queries and models

### Integration Testing
- Test API endpoints
- Test WebSocket communication
- Test database integration

### End-to-End Testing
- Test complete user flows
- Verify real-time functionality
- Test across different browsers

## 10. Deployment Considerations

### Cloud Hosting Options
- **AWS**: EC2 or Elastic Beanstalk
- **Google Cloud**: App Engine or Compute Engine
- **Heroku**: For simpler deployment
- **Vercel/Netlify**: For frontend hosting

### Deployment Architecture
```mermaid
graph TD
    A[Git Repository] --> B[CI/CD Pipeline]
    B --> C[Build Process]
    C --> D[Frontend Deployment]
    C --> E[Backend Deployment]
    E --> F[Database Setup]
    D --> G[CDN]
    E --> H[API Server]
    H --> I[Database]
```

### Scaling Considerations
- Implement connection pooling for database
- Consider Redis for session management if needed
- Use load balancing for multiple instances
- Implement proper error handling and logging

## 11. Error Handling Strategy

- Implement global error handling middleware
- Use try/catch blocks for async operations
- Create consistent error response format
- Log errors with appropriate severity levels
- Display user-friendly error messages on frontend