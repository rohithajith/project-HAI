# Changelog

## [Unreleased]

### Added
- Implemented a multi-agent system for hotel guest interactions
- Created BaseAgent class with common functionality for all agents
- Developed AgentManager for coordinating between different agents
- Implemented SupervisorAgent for routing requests to specialized agents
- Added RoomServiceAgent for handling room service requests
- Added MaintenanceAgent for managing maintenance issues
- Implemented WellnessAgent for spa and wellness-related inquiries
- Integrated RAG (Retrieval-Augmented Generation) for improved responses

### Changed
- Updated the language model loading process to use 8-bit quantization and automatic device selection
- Modified response generation to handle longer inputs and improve output quality

## Project Status

### System Flow
1. User input is received through the FastAPI endpoint
2. AgentManager processes the input and determines which agent should handle the request
3. If the input matches specific keywords, it's routed directly to the appropriate agent (fast path)
4. Otherwise, the SupervisorAgent selects the most suitable agent based on the input
5. The selected agent processes the request, potentially using RAG for information retrieval
6. The agent generates a response and any necessary tool calls
7. The response is logged and returned to the user

### Agents

#### BaseAgent
- Abstract base class for all agents
- Provides common functionality like response generation and output formatting
- Uses the language model to generate responses based on input and system prompts

#### AgentManager
- Coordinates between different agents
- Implements fast path routing for common requests
- Handles error cases and logging

#### SupervisorAgent
- Routes requests to specialized agents based on keywords and agent priorities
- Handles general inquiries when no specialized agent is suitable

#### RoomServiceAgent
- Handles food, drink, and amenity requests
- Uses RAG to provide information about menu items and services

#### MaintenanceAgent
- Manages maintenance issues and repair requests
- Logs maintenance notifications for hotel staff

#### WellnessAgent
- Handles spa bookings and wellness-related inquiries
- Uses RAG to check spa availability and provide information about wellness services

### Testing Process
## How to Run and Test

### Starting the Application
To start the main application, follow these steps:

1. Ensure you have all the required dependencies installed:
   ```
   pip install -r requirements.txt
   ```

2. Navigate to the project root directory and run:
   ```
   python backend/main.py
   ```

3. The server should start, and you'll see a message indicating it's running on `http://0.0.0.0:8001`.

### Testing with curl
You can test the different agents using curl commands. Here are some examples:

1. Test the WellnessAgent:
   ```
   curl -X POST "http://localhost:8001/chat" -H "Content-Type: application/json" -d '{"content": "I'd like to book a massage at the spa"}'
   ```

2. Test the RoomServiceAgent:
   ```
   curl -X POST "http://localhost:8001/chat" -H "Content-Type: application/json" -d '{"content": "Can I order a burger and fries to my room?"}'
   ```

3. Test the MaintenanceAgent:
   ```
   curl -X POST "http://localhost:8001/chat" -H "Content-Type: application/json" -d '{"content": "The air conditioning in my room is not working"}'
   ```

4. Test a general inquiry (handled by SupervisorAgent):
   ```
   curl -X POST "http://localhost:8001/chat" -H "Content-Type: application/json" -d '{"content": "What are the check-out times?"}'
   ```

After running these tests, check the `logs` directory for the generated log files to see the structured output from each agent.

### Agent Logic

#### RoomServiceAgent
- Keywords: "towel", "food", "drink", "order", "burger", "fries"
- Uses RAG to retrieve menu information and hotel policies
- Simulates order placement and towel requests

#### MaintenanceAgent
- Keywords: "broken", "repair", "fix", "not working", "schedule maintenance"
- Creates maintenance notifications with issue type and description
- Simulates scheduling of maintenance appointments

#### WellnessAgent
- Keywords: "wellness", "spa", "massage", "yoga", "fitness", "relax", "meditation"
- Uses RAG to check spa availability and retrieve wellness service information
- Simulates spa booking process and provides information about wellness facilities

#### SupervisorAgent
- Handles general inquiries not covered by specialized agents
- Uses a keyword-based approach to select the most appropriate agent
- Falls back to general response generation if no specialized agent is suitable

### RAG Implementation
- Utilizes a SimpleRAGHelper class to perform keyword-based search on hotel information
- Retrieves relevant passages from the hotel information document
- Incorporates retrieved information into the system prompt for more accurate and context-aware responses

This changelog reflects the current state of the project, including the implemented agents, their logic, and the overall system flow. As the project evolves, new entries should be added to document further changes and improvements.
