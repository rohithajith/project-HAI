# Hotel AI Assistant with LangGraph Multi-Agent System

This project enhances the Hotel Management System with a sophisticated AI assistant powered by LangGraph for multi-agent workflows and Pydantic-AI for Retrieval argument generation for retriving db, vectors, memory and  schemaenforcement.

## Features

- **Multi-Agent Architecture**: Specialized agents for different hotel services
  - Check-in Agent: Handles guest check-ins, verifies ID and payment
  - Room Service Agent: Processes room service requests
  - Wellness Agent: Provides wellness services like guided meditation
  - sevices booking agent to book spa, meeting rooms, co wokring space 
  - promption agent to promote theme nights , happy hours based on RAG , admins will upload .txt file for this 
  - And many more specialized agents
  - 
*we need indivitual agents and every agent gets a specialised prompt when triggered controlling the output via code or prompt.  
- **LangGraph Workflow**: Coordinated by a supervisor agent that routes requests to the appropriate specialized agent

- **Pydantic-AI Schemas**: RAG agents for promo policy rules of hotel retrival and more 

- **GDPR Compliance**: Built-in privacy and consent management and harmfull conent sensoring **strictly cannot produce LGBTQ, RAPE, BOMB, POLITICS OR ANY OTHER HARFMFULL CONTENT 

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │
│  FLASK Frontend │◄────►  flask Backend│
│                 │     │                 │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │                 │
         └─────────────►│ FastAPI Server  │
                        │  (name- LangGraph
                        )    │
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
## make sure the langgraph or pydantic ai is using local only , never use api calls as we want everything local

## Usage

### Starting the System

To start the entire system as Python FastAPI server with backend-starting and i want frontend in flask 
```
### Using the AI Assistant

The AI assistant is accessible through the chatbot interface in the frontend for guest & admin . It can help with:

1. **Guest Check-ins**: Verify ID and payment, assign rooms
2. **Room Service Requests**: Order towels, pillows, and other amenities
3. **Entertainment**: Access sleep stories and meditations
4. **Cab Booking**: Arrange transportation
5. **Wellness Services**: Guided meditation and breathing exercises
6. **And much more!**

## Project structure - no project structure for now 
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

#### flask Backend

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
*improve more 

## Privacy and GDPR Compliance

This system includes built-in features for GDPR compliance:

- **Consent Management**: Track user consent for data collection
- **Data Anonymization**: Anonymize personally identifiable information
- **Data Retention**: Automatically delete data after the retention period
- **Data Access Control**: Log all access to user data
- **Data Subject Rights**: Support for access and deletion requests

