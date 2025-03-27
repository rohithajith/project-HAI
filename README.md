# Project HAI: An Agentic AI Framework for Hotel Operations Automation

## Abstract

Project HAI represents a paradigm shift in hotel management, leveraging a sophisticated agentic AI framework built upon Large Language Models (LLMs) to automate and streamline administrative and guest service tasks. This system integrates a multi-agent backend with a user-friendly frontend interface, designed to handle diverse hotel operations, from real-time alerts and booking management to intelligent guest interactions and automated task delegation (e.g., laundry notifications, spa bookings, maintenance requests). By employing specialized AI agents coordinated by a supervisor, Project HAI aims to enhance operational efficiency, reduce staff workload, and elevate the guest experience through seamless, intelligent automation.

## Vision

The core vision of Project HAI is to revolutionize hotel administration by deploying autonomous AI agents capable of managing complex workflows. When a guest requests a service or an internal need arises, the system intelligently routes the task to the appropriate agent (e.g., Room Service Agent, Maintenance Agent, Concierge Agent). These agents then execute the necessary actions, interact with relevant hotel systems (simulated or real), and communicate updates, effectively automating processes like notifying laundry teams, scheduling spa appointments, logging maintenance issues, and fulfilling guest requests, thereby creating a highly responsive and efficient hotel ecosystem.

## Key Features & Capabilities

*   **Agentic Backend Architecture**: Employs a supervisor-agent model where an `AgentManager` routes tasks to specialized agents (e.g., `RoomServiceAgent`, `MaintenanceAgent`) based on request analysis.
*   **Automated Task Delegation**: Designed to automate tasks such as:
    *   Sending targeted notifications (e.g., laundry alerts to specific staff/rooms).
    *   Processing room service orders.
    *   Logging and prioritizing maintenance requests.
    *   Handling guest inquiries via an AI assistant.
*   **Real-time Alert System**: Frontend counter dynamically updates based on backend alert triggers via WebSockets.
*   **Integrated Booking Management**: Connects to a database (SQLite/PostgreSQL) to display and manage booking information, categorized by status (upcoming, current, past).
*   **AI Chatbot Assistant**: Provides an interactive interface for guests, powered by:
    *   Locally hosted, fine-tuned models (e.g., GPT-2 based `finetunedmodel-merged`) for offline capability and data privacy.
    *   Optional integration with external APIs (e.g., Hugging Face).
    *   Customizable system prompts for tailored hotel persona and responses.
*   **Real-time Communication**: Utilizes Socket.IO for seamless bidirectional communication between frontend and backend.

## System Architecture

Project HAI utilizes a modern full-stack architecture optimized for real-time interaction and intelligent processing:

*   **Frontend**: React.js with Material-UI for a responsive and intuitive user interface.
*   **Backend**: Node.js with Express.js, featuring a core `AgentManager` and specialized AI agents.
*   **AI Agents**: JavaScript-based agents (`RoomServiceAgent`, `MaintenanceAgent`, etc.) orchestrated by `AgentManager`.
*   **LLM Integration**: Python scripts (`local_model_chatbot.py`, `chatbot_bridge.py`) interface with local or remote LLMs for natural language understanding and generation.
*   **Database**: Supports SQLite (`hotel_bookings.db`) for ease of setup and PostgreSQL for scalability.
*   **Real-time Layer**: Socket.IO enables instantaneous updates and notifications.

### Backend Agentic Workflow

The backend employs a supervisor pattern where the `AgentManager` acts as the central orchestrator. Upon receiving a user request (typically via the chatbot or specific UI actions), the following flow is initiated:

1.  **Request Reception**: The backend receives the user message and conversation history.
2.  **Supervisor Analysis**: The `AgentManager` analyzes the message content and context to determine the user's intent.
3.  **Agent Routing**: Based on the identified intent, the `AgentManager` routes the request to the most appropriate specialized agent (e.g., `RoomServiceAgent` for food orders, `MaintenanceAgent` for repair requests).
4.  **Agent Execution**: The selected agent processes the request. This may involve:
    *   Extracting key information (e.g., room number, specific items, issue details).
    *   Utilizing predefined tools or functions (e.g., `order_food`, `report_issue`).
    *   Generating internal notifications or alerts (e.g., via `notificationService`).
    *   Formulating a response for the user.
5.  **Fallback Mechanism**: If no specialized agent can handle the request, the `AgentManager` defaults to a general-purpose LLM interaction (via `local_model_chatbot.py`) to provide an informative response.
6.  **Response Delivery**: The final response (generated by an agent or the fallback LLM) is sent back to the user interface.

The following diagram illustrates this workflow:

```mermaid
graph TD
    A[User Request] --> B{Agent Manager (Supervisor)};
    B -- Intent Analysis --> C{Route to Agent};
    C -- Intent: Room Service --> D[Room Service Agent];
    C -- Intent: Maintenance --> E[Maintenance Agent];
    C -- Intent: Other/General --> F[General LLM (Fallback)];
    D -- Uses Tool --> G[Tool Execution (e.g., Order Food)];
    E -- Uses Tool --> H[Tool Execution (e.g., Report Issue)];
    G --> I[Agent Response/Action];
    H --> I;
    F --> I;
    I --> J[Response to User];
```

## Prerequisites

*   Node.js (v14 or higher recommended)
*   npm (v6 or higher) or yarn
*   Python (v3.8 or higher, for chatbot features)
*   Git

## Quick Start Guide

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd project-HAI
    ```

2.  **One-command setup and run (Installs all dependencies and starts)**:
    ```bash
    npm run setup-and-start
    ```
    *(Note: Ensure Python environment is set up for chatbot features if needed. See `CHATBOT_SETUP.md`)*

## Manual Installation

1.  **Install Root Dependencies**:
    ```bash
    npm install
    ```

2.  **Install Backend & Frontend Dependencies**:
    ```bash
    npm run install:all
    ```

3.  **Setup Python Environment (for Chatbot)**:
    *   Navigate to the `backend` directory.
    *   Create a virtual environment: `python -m venv venv`
    *   Activate the environment (e.g., `source venv/bin/activate` on Linux/macOS, `.\venv\Scripts\activate` on Windows).
    *   Install Python dependencies: `pip install -r ../requirements.txt`
    *   Refer to `CHATBOT_SETUP.md` and `LOCAL_MODEL_README.md` for detailed model setup.

4.  **Configure Environment Variables**:
    *   Review and modify `.env` files in the `backend` directory as needed (defaults provided).

5.  **Database Setup**:
    *   **SQLite (Default)**: The `hotel_bookings.db` file is included. No setup needed initially. It will be created/recreated if missing.
    *   **PostgreSQL (Optional)**: Refer to `POSTGRESQL_IMPLEMENTATION.md` for setup instructions.

6.  **Start the Application**:
    ```bash
    npm start
    ```

## Accessing the Application

*   **Frontend**: [http://localhost:3000](http://localhost:3000)
*   **Backend API**: [http://localhost:5000/api](http://localhost:5000/api)

## Development

### Running Components Separately

```bash
# Start backend only (with auto-restart on changes)
npm run dev:backend

# Start frontend only (React development server)
npm run start:frontend
```
*(Note: `dev:backend` uses `nodemon`, ensure it's installed: `npm install -g nodemon` or run via `npx nodemon server.js`)*

### Project Structure Overview

```
project-HAI/
├── frontend/                  # React frontend application
│   └── src/
│       ├── components/        # UI components (Alerts, Bookings, Chatbot, Auth, etc.)
│       ├── contexts/          # React Context API for state management
│       ├── pages/             # Top-level page components
│       └── services/          # API and WebSocket service integrations
│
├── backend/                   # Node.js backend application
│   ├── ai_agents/             # Core AI agent logic (Manager, Specific Agents)
│   ├── config/                # Configuration (database connections)
│   ├── controllers/           # Express route handlers
│   ├── middleware/            # Express middleware (e.g., authentication)
│   ├── models/                # Database models/schemas (if using an ORM)
│   ├── routes/                # API route definitions
│   ├── services/              # Business logic (notifications, sockets, DB interactions)
│   ├── scripts/               # Utility and setup scripts
│   ├── chatbot_bridge.py      # Python bridge for LLM communication
│   ├── local_model_chatbot.py # Logic for local LLM interaction
│   └── server.js              # Main server entry point
│
├── hotel_bookings.db          # Default SQLite database file
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── package.json               # Root project configuration and scripts
```

## API Endpoints & WebSocket Events

*(Existing API and WebSocket details remain largely the same but could be updated based on agent interactions if necessary. Keeping the original list for now.)*

### Bookings API
*   `GET /api/bookings` - Get all bookings
*   `GET /api/bookings/upcoming` - Get upcoming bookings
*   `GET /api/bookings/current` - Get current bookings
*   `GET /api/bookings/past` - Get past bookings
*   `GET /api/bookings/:id` - Get booking by ID

### Alerts API
*   `GET /api/alerts` - Get alert history
*   `GET /api/alerts/count` - Get current alert count
*   `POST /api/alerts` - Create a new alert
*   `PUT /api/alerts/:id/resolve` - Resolve an alert
*   `POST /api/alerts/reset` - Reset alert counter

### Notifications API
*   `GET /api/notifications` - Get all notifications
*   `POST /api/notifications` - Create a new notification
*   `GET /api/notifications/room/:roomNumber` - Get notifications for a specific room
*   `PUT /api/notifications/:id/read` - Mark a notification as read
*   `POST /api/notifications/laundry` - Send a laundry alert notification

### WebSocket Events (Server -> Client)
*   `alert_count_updated` - Broadcast updated alert count
*   `new_booking` - Broadcast when a new booking is added
*   `booking_updated` - Broadcast when a booking is updated
*   `new_notification` - Send targeted notification

### WebSocket Events (Client -> Server)
*   `trigger_alert` - Client triggers an alert
*   `send_notification` - Send a notification to specific room(s)
*   `join_room` - Join a specific notification room
*   `chat_message` (Implicitly handled by chatbot/agent system)

## Troubleshooting

*(Keep existing troubleshooting section)*

1.  **Port conflicts**: If ports 3000 or 5000 are already in use, you can modify the port in:
   - Backend: Edit `PORT` in `backend/.env`
   - Frontend: Create a `.env` file in the frontend directory with `PORT=3001`

2.  **Database errors**: If you encounter database errors, try deleting the `hotel_bookings.db` file and restart the application (for SQLite). Check PostgreSQL connection details if using Postgres.

3.  **Missing dependencies**: If you encounter errors about missing modules, run:
   ```bash
   npm run install:all
   ```
   And ensure Python dependencies are installed:
   ```bash
   # In backend directory with activated venv
   pip install -r ../requirements.txt
   ```

4.  **Chatbot Model Issues**: Refer to `CHATBOT_SETUP.md` and `LOCAL_MODEL_README.md`. Ensure Python environment and dependencies are correct. Check model download/path.

## License

This project is licensed under the ISC License.