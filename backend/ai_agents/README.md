# Hotel AI Assistant Multi-Agent System

This package implements a multi-agent system for a hotel assistant using LangGraph for workflow management and Pydantic-AI for schema enforcement.

## Features

- **Multi-Agent Architecture**: Specialized agents for different hotel services
- **LangGraph Workflow**: Coordinated by a supervisor agent
- **Pydantic-AI Schemas**: Strong typing and validation for agent communication
- **FastAPI Server**: REST API and WebSocket interface
- **GDPR Compliance**: Built-in privacy and consent management

## Installation

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy the example environment file and configure it:

```bash
cp .env.example .env
# Edit .env with your configuration
```

## Usage

### Starting the Server

Run the FastAPI server:

```bash
python run.py
```

The server will start on http://localhost:8000 by default.

### API Endpoints

- `POST /api/chat`: Process a chat message
- `WebSocket /ws/{conversation_id}`: Real-time chat
- `GET /api/conversations/{conversation_id}`: Get conversation history
- `DELETE /api/conversations/{conversation_id}`: Delete a conversation
- `GET /api/health`: Health check

### Example API Request

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "messages": [
            {"role": "user", "content": "I'd like to check in to my room"}
        ]
    }
)

print(response.json())
```

## Architecture

### Components

- **Supervisor**: Central agent that routes messages to specialized agents
- **Agents**: Specialized agents for different hotel services
  - `CheckInAgent`: Handles guest check-ins
  - `RoomServiceAgent`: Processes room service requests
  - `WellnessAgent`: Provides wellness services
- **Schemas**: Pydantic models for agent communication
- **Tools**: Functions for interacting with external systems
- **Services**: Database and external service integrations
- **Utils**: Utility functions

### Agent Workflow

1. User sends a message to the system
2. Supervisor analyzes the message and routes it to the appropriate agent
3. Agent processes the message and generates a response
4. Response is returned to the user
5. Any actions are logged in the database

## Development

### Adding a New Agent

1. Create a new agent class in `agents/` that extends `BaseAgent`
2. Define input and output schemas in `schemas/agent_schemas.py`
3. Implement the `process` method to handle messages
4. Add the agent to the supervisor in `supervisor.py`

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

### Adding a New Tool

1. Create a new function in `tools/` that implements the tool
2. Add the tool to the appropriate agent

Example:

```python
def my_new_tool(param1: str, param2: int) -> Dict[str, Any]:
    """Description of my new tool.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        The result of the tool
    """
    # Implement the tool
    # ...
    return result
```

## Privacy and GDPR Compliance

This system includes built-in features for GDPR compliance:

- **Consent Management**: Track user consent for data collection
- **Data Anonymization**: Anonymize personally identifiable information
- **Data Retention**: Automatically delete data after the retention period
- **Data Access Control**: Log all access to user data
- **Data Subject Rights**: Support for access and deletion requests

## Testing

Run the tests:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.