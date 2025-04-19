# AI Agents System (`backend/ai_agents`)
 It utilizes a supervisor-worker pattern where a `SupervisorAgent` routes requests to specialized agents based on the user's message content and predefined priorities.

## Core Components

*   **`BaseAgent` (`base_agent.py`):**
    *   An abstract base class defining the standard interface for all specialized agents.
    *   Provides common functionalities:
        *   Tool definition and handling (`ToolDefinition`, `get_available_tools`, `handle_tool_call`).
        *   Standardized output structure as a json object by the agents (`AgentOutput`).
        *   Utility methods for structuring the output based on the user input.
*   **`AgentManager` (`agent_manager.py`):**
    *   The main entry point for processing user messages within the agent system.
    *   Initializes and registers all specialized agents with the `SupervisorAgent`.
    *   Loads the local language model and tokenizer, passing them to the agents.
    *   Implements a "fast path" routing: If a message contains specific keywords related to common room service requests (e.g., "towel", "food", "order", "burger"), it directly calls the `RoomServiceAgent`.
    *   For other messages, it delegates processing to the `SupervisorAgent`.
    *   Includes top-level error handling.
*   **`SupervisorAgent` (`supervisor_agent.py`):**
    *   Acts as the central router or coordinator.
    *   Maintains a registry of all specialized agents.
    *   Implements `_select_next_agent(message, history)` logic:
        1.  Checks for direct keyword matches defined in `agent_keyword_map`.
        2.  If no keyword match, iterates through registered agents, calling their `should_handle` method.
        3.  Selects the agent with the highest `priority` among those that can handle the request.
    *   Calls the `process` method of the selected specialized agent.
    *   Handles cases where no suitable agent is found.
    *   Includes error handling for the routing and agent processing steps.

## Specialized Agents

These agents inherit from `BaseAgent` and handle specific domains:
all agents will tackle the input given by suporvisor / agentmanager and produce a json object with the given input 
*   **`CheckInAgent` (`checkin_agent.py`):**
    *   **Purpose:** Manages guest check-in processes.
    *   **Keywords:** "check in", "arrival", "booking", "reservation", "room key".
    *   **Tools:** `verify_id`.
    *   **Notes:** Agent checks in the hotel_bookings.db to check the id is existing or not and  guides users through check-in steps or verifies existing bookings.
*   **`MaintenanceAgent` (`maintenance_agent.py`):**
    *   **Purpose:** Handles guest reports of maintenance issues and scheduling requests.
    *   **Keywords:** "broken", "repair", "fix", "not working", "schedule maintenance".
    *   **Tools:** `report_issue`, `schedule_maintenance`.
    *   **Notes:** Use notification [] array and add the notification into it everytiime its called / service to report issues.
*   **`RoomServiceAgent` (`room_service_agent.py`):**
    *   **Purpose:** Handles requests for room service (food, drinks, towels, amenities).
    *   **Keywords:** "room service", "food", "drink", "towel", "order", "burger", "fries".
    *   **Tools:** `check_menu_availability`, `place_order`.
    *   **Notes:** Has high priority. Can be called directly by `AgentManager` for specific keywords (fast path). add request to notifications [] array when triggered.
*   **`ServicesBookingAgent` (`services_booking_agent.py`):**
    *   **Purpose:** Manages bookings for hotel services like meeting rooms and co-working spaces.
    *   **Keywords:** "meeting room", "book", "reserve", "workspace", "conference room".
    *   **Tools:**  `check_service_availability`, `create_booking`
    *   **Notes:** create_booking will add request to notifications [] array when triggered.
*   **`WellnessAgent` (`wellness_agent.py`):**
    *   **Purpose:** Handles requests related to wellness services (spa, yoga, meditation, fitness).
    *   **Keywords:** "wellness", "meditation", "yoga", "fitness", "spa", "relax".
    *   **Tools:**  `book_session`.
    *   **Notes:** book_session will add add request to notifications [] array when triggered.


## Supporting Modules


*   **`ErrorHandler` (`error_handler.py`):** Defines custom exceptions (`AgentError`, etc.) and provides a centralized `ErrorHandler` class for logging errors and generating standardized user-facing error responses.
## Interaction Flow

1.  A user message enters the system via `AgentManager.process`.
2.  **Fast Path Check:** `AgentManager` checks if the message contains specific room service keywords (e.g., "towel", "order", "burger").
    *   **If YES:** It directly calls `RoomServiceAgent.process`.
    *   **If NO:** It proceeds to delegate to the supervisor.
3.  **Delegation:** `AgentManager` calls `SupervisorAgent.process`.
4.  **Agent Selection:** `SupervisorAgent._select_next_agent` determines the best agent:
    *   It first checks for keyword matches defined within the supervisor.
    *   If no keyword match, it calls `should_handle` on all registered agents.
    *   It selects the highest priority agent that returns `True` from `should_handle`.
5.  **Agent Processing:** `SupervisorAgent` calls the `process` method of the selected agent (if any).
    *   If no agent is selected, the supervisor returns a default message indicating it cannot handle the request.
6.  **Response:** The specialized agent processes the request (potentially using tools, content filtering) and returns an `AgentOutput`.
* **note** make sure to avoid where query is in loops with agents again and again 
8.  **Formatting (Post-Processing):** The `OutputFormattingAgent` might be used by the application layer (outside this directory) to format the final `AgentOutput` before sending it to the user/frontend.

Throughout this flow, errors are caught and handled by the `ErrorHandler`, interactions can be logged by `AgentLogger`, and performance is monitored by `MonitoringSystem`. Content safety is checked via `ContentFilter` within the agents.

## Data Protection and Privacy Features

The system implements comprehensive GDPR and LESP (Legal, Ethical, Social, and Privacy) compliance features to ensure proper handling of user data:

### Content Filtering

* **`BaseAgent` (`base_agent.py`):**
  * Implements `filter_input` and `filter_output` methods to detect and filter offensive, political, or sensitive content
  * Uses regex pattern matching across three categories: offensive, political, and sensitive
  * Provides safe alternative responses when content is filtered

* **`AgentManager` (`agent_manager.py`):**
  * Implements filtering at the entry point before messages are routed to agents
  * Ensures filtering happens even before agent selection
  * Filters error messages to prevent sensitive information leakage

### Data Privacy and GDPR Compliance

* **`ConversationMemory` (`conversation_memory.py`):**
  * Implements personal data anonymization for user messages
  * Adds GDPR metadata to conversation records (purpose, retention period, consent status)
  * Provides methods for data subject rights (access, delete, update)
  * Organizes data storage by date for better retention management
  * Implements automated data retention with expiration dates

* **`RoomServiceAgent` (`room_service_agent.py`):**
  * Implements anonymization of personal data in logs
  * Adds GDPR metadata to logged data
  * Implements data minimization by only storing necessary fields

* **`DataProtectionManager` (`data_protection.py`):**
  * Provides automated data cleanup based on retention periods
  * Implements data protection impact assessment
  * Maintains records of data processing activities
  * Runs scheduled tasks for regular cleanup and assessment

### API Endpoints for GDPR Compliance

* **Privacy Notice:** `/api/privacy/notice` - Returns the privacy notice with consent options
* **Data Access:** `/api/user/data/{conversation_id}` - Allows users to access their data
* **Data Deletion:** `/api/user/data/{conversation_id}` - Allows users to delete their data
* **Data Correction:** `/api/user/data/{conversation_id}/{message_id}` - Allows users to correct their data
* **Consent Management:** `/api/user/consent/{conversation_id}` - Updates user consent preferences
* **Data Export:** `/api/user/data/export/{conversation_id}` - Exports user data in a portable format

These features ensure the system complies with key GDPR principles while maintaining its functionality.