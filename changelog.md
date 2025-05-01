# Changelog

## [Unreleased]

### Changed
- Enhanced SupervisorAgent to output structured JSON responses with agent selection reasoning
- Updated supervisor_prompt.txt and supervisor_default_prompt.txt to instruct LLM to return JSON format
- Modified SupervisorAgent's process method to parse and handle structured JSON responses
- Updated AgentManager to properly handle the new structured responses
- Fixed BaseAgent's load_prompt method to correctly handle both description and prompt file paths
- Updated all agent classes to use the correct path format for loading prompt files
- Fixed path resolution for description files to properly locate them from the project root
- Simplified SupervisorAgent to use a more robust approach for agent selection
- Updated supervisor_prompt.txt and supervisor_default_prompt.txt to use a simpler format
- Implemented a fallback mechanism to extract agent names from conversational responses
- Added detailed logging to help diagnose routing issues

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
- Updated frontend README with project-specific details.

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


18/04/25

 implemented content filtering methods in the BaseAgent class to prevent the model from outputting offensive, political, or sensitive responses. Here's what I added:

Input Filtering System:

Added a filter_input method that scans user messages for problematic content
If detected, it replaces the input with a safe alternative
Output Filtering System:

Added a filter_output method that scans model responses for problematic content
If detected, it replaces the output with a safe, hotel-appropriate response
Content Categories:

Offensive: Hate speech, profanity, violent terms, etc.
Political: Political figures, ideologies, elections, etc.
Sensitive: Illegal activities, weapons, hacking, etc.
Implementation Details:

Used regular expressions for pattern matching
Created separate pattern lists for each category for easy maintenance
Added helper methods to provide safe alternative responses
Modified the generate_response method to apply filtering at both input and output stages
This implementation provides a two-layer defense:

First, it prevents problematic user inputs from reaching the model
Second, it filters any potentially problematic model outputs before they reach the user

## 
Updated the room_service_agent.py file:

Added anonymization of personal data in the _save_to_log function
Added GDPR metadata to logged data (purpose, retention period, consent reference)
Implemented data minimization by only storing necessary fields
Organized logs by date for easier retention management
Updated the conversation_memory.py file:

Added anonymization of personal data in user messages
Added GDPR metadata to conversation records
Implemented consent management
Added data subject rights implementation (access, delete, update)
Implemented automated data retention
Added GDPR compliance endpoints to main.py:

Added endpoints for accessing, deleting, and updating user data
Added endpoint for updating consent preferences
Added endpoint for exporting user data in a portable format
Added endpoint for getting the privacy notice
Created a new data_protection.py file:

Implemented automated data cleanup based on retention periods
Added data protection impact assessment
Added data processing records
Implemented scheduled tasks for regular cleanup and assessment
Updated main.py to start the data protection scheduled tasks when the server starts

These changes ensure that the project is compliant with GDPR and LESP requirements, including:

Data minimization: Only collecting and storing necessary data
Purpose limitation: Documenting why data is stored and used
Storage limitation: Setting retention periods and automatically deleting expired data
Data subject rights: Allowing users to access, correct, and delete their data
Consent management: Tracking and respecting user consent preferences
Data security: Anonymizing personal data and implementing access controls
Data processing records: Keeping records of data processing activities
Data protection impact assessment: Assessing risks to user rights and freedoms


# added checkin_agent 
Check-in Agent Enhanced with Stay Extension Feature:

Key Additions:

Implemented _handle_extend_stay() method for checking room availability
Added dynamic room availability checking logic
Enhanced keyword detection for stay extension requests
Features:

Check booking details by ID
Validate room availability for stay extension
Provide contextual responses based on room availability

# added sos emergency 
BaseAgent now provides a default empty implementation of get_keywords()
Added a default handler for the notify_admin_dashboard tool
Kept the existing emergency detection and routing logic
The system can now:

Detect emergency keywords
Classify emergency types
Notify the admin dashboard
Provide an immediate response to the guest
Emergency Detection Workflow:

User sends an SOS-related message
AgentManager detects emergency keywords
SOSAgent processes the request
Emergency metadata is generated
Admin dashboard is notified
Guest receives an immediate, reassuring response
The implementation supports various emergency types, including fire, medical emergencies, mental health crises, and personal safety concerns.