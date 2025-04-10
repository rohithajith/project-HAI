# Backend Implementation Plan

## Directory Structure

```
backend/
├── ai_agents/
│   ├── __init__.py
│   ├── base_agent.py
│   ├── agent_manager.py
│   ├── supervisor_agent.py
│   ├── checkin_agent.py
│   ├── maintenance_agent.py
│   ├── promotion_agent.py
│   ├── room_service_agent.py
│   ├── services_booking_agent.py
│   └── wellness_agent.py
├── utils/
│   ├── __init__.py
│   ├── error_handler.py
│   └── content_filter.py
└── main.py
```

## Core Components Implementation

### 1. base_agent.py

- Implement `BaseAgent` abstract base class
- Define `ToolDefinition`, `AgentOutput`, and utility methods

### 2. agent_manager.py

- Implement `AgentManager` class
- Load local language model and tokenizer (use code from teste.py)
- Implement fast path routing for room service requests
- Implement main processing logic

### 3. supervisor_agent.py

- Implement `SupervisorAgent` class
- Implement agent selection logic
- Handle routing and error cases

### 4. Specialized Agents

For each specialized agent (CheckInAgent, MaintenanceAgent, PromotionAgent, RoomServiceAgent, ServicesBookingAgent, WellnessAgent):

- Inherit from `BaseAgent`
- Implement `should_handle` method
- Implement `process` method
- Define and implement necessary tools

### 5. error_handler.py

- Define custom exceptions
- Implement `ErrorHandler` class for logging and generating error responses

### 6. content_filter.py

- Implement content filtering logic to ensure appropriate responses

### 7. main.py

- Set up FastAPI application
- Implement endpoint for processing user messages
- Initialize AgentManager and handle incoming requests

## Implementation Notes

1. Use the local model loading code from teste.py in the AgentManager.
2. Implement the fast path routing for room service requests in the AgentManager.
3. Ensure all agents return responses in the specified JSON format.
4. Implement proper error handling and logging throughout the system.
5. Use the hotel_bookings.db for the CheckInAgent to verify bookings.
6. Implement RAG with embeddings for the PromotionAgent using data from data/policy.txt.
7. Add notifications to an array for relevant agent actions (Maintenance, RoomService, ServicesBooking, Wellness).
8. Avoid query loops between agents by implementing proper routing logic in the SupervisorAgent.

## Testing Plan

1. Create unit tests for each agent and core component.
2. Implement integration tests to ensure proper interaction between components.
3. Create end-to-end tests simulating user interactions for various scenarios.

## Next Steps

1. Implement the core components (BaseAgent, AgentManager, SupervisorAgent).
2. Develop specialized agents one by one, starting with the RoomServiceAgent (high priority).
3. Implement utility modules (ErrorHandler, ContentFilter).
4. Set up the main FastAPI application.
5. Conduct thorough testing and refine as needed.