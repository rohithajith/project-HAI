# Hotel AI Frontend

## Architecture Overview

The Hotel AI Frontend is designed with a modular, scalable architecture supporting three primary interfaces:
- Guest Chatbot Interface
- Combined Admin & Room Service Dashboard

### Key Components

1. **WebSocket Client** (`websocket_client.js`)
   - Unified WebSocket communication
   - Robust connection management
   - Namespace support

2. **Notification Service** (`notification_service.js`)
   - Centralized notification handling
   - Multiple notification categories
   - Priority-based notification management

3. **Guest Interface** (`guest_interface.js`)
   - Room number validation
   - Real-time chat functionality
   - WebSocket communication

4. **Combined Dashboard** (`combined_dashboard.js`)
   - Admin and Room Service interfaces
   - Request management
   - Real-time notifications

## Setup and Installation

### Prerequisites
- Node.js (v16+ recommended)
- npm (v8+)

### Installation Steps
1. Clone the repository
2. Navigate to the frontend directory
3. Install dependencies:
   ```bash
   npm install
   ```

### Development
Run the development server:
```bash
npm start
```

### Build for Production
Create production build:
```bash
npm run build
```

### Testing
Run test suite:
```bash
npm test
```

## Configuration

### Environment Variables
- `BACKEND_URL`: Backend server URL (default: `http://localhost:5000`)
- `PORT`: Frontend development server port (default: `3000`)

## WebSocket Namespaces
- `/guest`: Guest chatbot communication
- `/admin-room-service`: Admin and Room Service dashboard

## Deployment
1. Build the project: `npm run build`
2. Deploy the contents of the `dist/` directory to your web server

## Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Minimum IE11 with polyfills

## Troubleshooting
- Ensure backend server is running
- Check browser console for WebSocket connection errors
- Verify network connectivity

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
MIT License