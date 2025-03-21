# Hotel AI Assistant with LangGraph Multi-Agent System

This project enhances the Hotel Management System with a sophisticated AI assistant powered by LangGraph for multi-agent workflows and Pydantic-AI for schema enforcement.

## Features

- **Multi-Agent Architecture**: Specialized agents for different hotel services
  - Check-in Agent: Handles guest check-ins, verifies ID and payment
  - Room Service Agent: Processes room service requests
  - Wellness Agent: Provides wellness services like guided meditation
  - And many more specialized agents

- **LangGraph Workflow**: Coordinated by a supervisor agent that routes requests to the appropriate specialized agent

- **Pydantic-AI Schemas**: Strong typing and validation for agent communication

- **GDPR Compliance**: Built-in privacy and consent management

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │
│  React Frontend │◄────►  Node.js Backend│
│                 │     │                 │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │                 │
         └─────────────►│ FastAPI Server  │
                        │  (LangGraph)    │
                        │                 │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │                 │
                        │  Multi-Agent    │
                        │    System       │
                        │                 │
                        └─────────────────┘
```

## Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- npm (v6 or higher)
- pip (v20 or higher)

## Installation

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd hotel-management-system
   ```

2. **Install dependencies**:
   ```
   npm run install:all
   npm run setup:langgraph
   ```

3. **Configure environment variables**:
   ```
   # Copy the example environment file for the Python FastAPI server
   cp backend/ai_agents/.env.example backend/ai_agents/.env
   
   # Edit the .env file with your OpenAI API key and other settings
   ```

## Usage

### Starting the System

To start the entire system (Node.js backend, React frontend, and Python FastAPI server):

```
npm run start:langgraph
```

This will start:
- The Node.js backend on port 5000
- The React frontend on port 3000
- The Python FastAPI server on port 8000

### Using the AI Assistant

The AI assistant is accessible through the chatbot interface in the frontend. It can help with:

1. **Guest Check-ins**: Verify ID and payment, assign rooms
2. **Room Service Requests**: Order towels, pillows, and other amenities
3. **Entertainment**: Access sleep stories and meditations
4. **Cab Booking**: Arrange transportation
5. **Wellness Services**: Guided meditation and breathing exercises
6. **And much more!**

## Development

### Project Structure

```
project-root/
├── frontend/                  # React frontend application
├── backend/                   # Node.js backend application
│   ├── ai_agents/             # LangGraph multi-agent system
│   │   ├── agents/            # Specialized agents
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── tools/             # Agent tools
│   │   ├── services/          # Services for external integrations
│   │   └── utils/             # Utility functions
│   ├── controllers/           # Request handlers
│   ├── routes/                # API routes
│   └── services/              # Business logic
├── start_langgraph_system.js  # Script to start all components
└── README_LANGGRAPH.md        # This file
```

### Adding a New Agent

1. Create a new agent class in `backend/ai_agents/agents/` that extends `BaseAgent`
2. Define input and output schemas in `backend/ai_agents/schemas/agent_schemas.py`
3. Implement the `process` method to handle messages
4. Add the agent to the supervisor in `backend/ai_agents/supervisor.py`

Example:

```python
from ..schemas import AgentInput, AgentOutput
from .base_agent import BaseAgent

class MyNewAgent(BaseAgent):
    def __init__(self, model_name: str = "gpt-4o"):
        super().__init__(
            name="my_new_agent",
            description="Description of my new agent"
        )
        # Initialize the agent
        
    @property
    def input_schema(self):
        return MyNewAgentInput
        
    @property
    def output_schema(self):
        return MyNewAgentOutput
        
    async def process(self, input_data: MyNewAgentInput) -> MyNewAgentOutput:
        # Process the input and generate output
        # ...
        return output
```

### API Endpoints

#### Node.js Backend

- `POST /api/chatbot`: Process a chat message
- `GET /api/chatbot/conversations/:conversation_id`: Get conversation history
- `DELETE /api/chatbot/conversations/:conversation_id`: Delete a conversation
- `GET /api/chatbot/health`: Health check

#### Python FastAPI Server

- `POST /api/chat`: Process a chat message
- `WebSocket /ws/{conversation_id}`: Real-time chat
- `GET /api/conversations/{conversation_id}`: Get conversation history
- `DELETE /api/conversations/{conversation_id}`: Delete a conversation
- `GET /api/health`: Health check

## Privacy and GDPR Compliance

This system includes built-in features for GDPR compliance:

- **Consent Management**: Track user consent for data collection
- **Data Anonymization**: Anonymize personally identifiable information
- **Data Retention**: Automatically delete data after the retention period
- **Data Access Control**: Log all access to user data
- **Data Subject Rights**: Support for access and deletion requests

## Troubleshooting

### Common Issues

1. **OpenAI API Key**: Make sure you have set the `OPENAI_API_KEY` environment variable in `backend/ai_agents/.env`

2. **Port Conflicts**: If ports 3000, 5000, or 8000 are already in use, you can modify them in the environment variables

3. **Python Dependencies**: If you encounter errors with Python dependencies, try:
   ```
   cd backend/ai_agents
   pip install -r requirements.txt
   ```

4. **Node.js Dependencies**: If you encounter errors with Node.js dependencies, try:
   ```
   npm run install:all
   ```

## License

This project is licensed under the ISC License.