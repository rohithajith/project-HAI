# Hotel AI Assistant System Architecture

This document outlines the architecture and flow of the Hotel AI Assistant system, which uses a hierarchical multi-agent system with local LLM integration.

## System Components

### 1. Agent System Core Components

#### Base Agent (`base_agent.py`)
- Abstract base class for all specialized agents
- Defines common functionality:
  - Content safety checking
  - Tool parameter handling
  - Message history management
  - Room number and booking reference extraction

#### Supervisor Agent (`supervisor_agent.py`)
- Coordinates workflow between specialized agents
- Uses LangGraph for agent orchestration
- Components:
  - State management via `SupervisorState`
  - Agent registration system
  - Message routing logic
  - Workflow compilation using `StateGraph`

#### Agent Manager (`agent_manager_corrected.py`)
- Manages the multi-agent system using local model
- Initializes and coordinates:
  - Local LLM model loading from 'finetunedmodel-merged'
  - Agent registration
  - Message processing
  - Error handling

### 2. Specialized Agents

#### Room Service Agent (`room_service_agent.py`)
- Handles room service and housekeeping requests
- Features:
  - Menu requests
  - Order processing
  - Status checking
  - Housekeeping requests (towels, amenities)
- Priority level: 8 (Medium-high)

### 3. Server Components

#### Flask Server (`flask_app.py`)
- WebSocket-based communication
- Components:
  - Event handling (connect, disconnect, message)
  - Message processing via agent system
  - Local model integration
  - Async operations using eventlet

#### FastAPI Server (`fastapi_server.py`)
- REST API endpoints
- Features:
  - Chat endpoints (HTTP and WebSocket)
  - Monitoring system
  - Health checks
  - Metrics collection
  - Alert management

## Message Flow

1. Client sends message via WebSocket/HTTP
2. Message received by Flask/FastAPI server
3. AgentManager processes message:
   - Loads local model from 'finetunedmodel-merged'
   - Routes message through SupervisorAgent
4. SupervisorAgent:
   - Determines appropriate specialized agent
   - Manages workflow using LangGraph
5. Specialized Agent (e.g., RoomServiceAgent):
   - Processes request
   - Generates response
6. Response returned to client

## Testing System (`test_agents.py`)

### Test Components
- TestAgentSystem class for integration testing
- Tests:
  - WebSocket connection
  - Message processing
  - Agent responses
  - Local model integration

### Test Flow
1. Loads local model
2. Establishes WebSocket connection
3. Sends test message ("hi, can i get towels")
4. Verifies:
   - Response received
   - Response contains expected content
   - Proper agent handling

### Example Test Case
```python
def test_room_service_request(self):
    """Test the room service request flow with all agents"""
    test_message = "hi, can i get towels"
    self.socketio_client.emit('message', {
        'message': test_message,
        'history': []
    })
    # Verifies response and checks towel request handling
```

## Local Model Integration

- Model Path: 'C:\Users\2312205\Downloads\project-HAI\finetunedmodel-merged'
- Loading: Handled by `local_model_chatbot.py`
- Features:
  - 8-bit quantization
  - Automatic device mapping
  - Thread-safe loading
  - Caching mechanism
## Monitoring System (`monitoring.py`)

### Metrics Collection
- System-wide metrics:
  - CPU usage
  - Memory usage
  - Requests per minute
  - Error rate
  - Response time
  - System uptime

### Agent-Specific Metrics
- Per-agent tracking:
  - Total requests
  - Successful requests
  - Failed requests
  - Average response time
  - Last error
  - Last active timestamp

### Alert System
- Configurable alert thresholds
- Alert types:
  - Performance alerts (CPU, Memory)
  - Error rate alerts
  - Response time alerts
- Alert management:
  - Severity levels
  - Acknowledgment system
  - Alert history

### Metric Storage
- Metrics saved to: `data/metrics/current_metrics.json`
- Automatic cleanup of old metrics (7-day retention)
- Background tasks:
  - Metric collection (every minute)
  - Cleanup routine (hourly)

### Health Monitoring
- System health status:
  - "healthy" (error rate < 5%)
  - "degraded" (error rate >= 5%)
- Agent health tracking:
  - Individual agent status
  - Error rates
  - Activity monitoring

## Error Handling System (`error_handler.py`)

### Error Types
- Base Error:
  - `AgentError`: Base exception for all agent-related errors
- Specialized Errors:
  - `ContentFilterError`: Content filtering violations
  - `ProcessingError`: Message processing failures
  - `ValidationError`: Input validation issues
  - `AuthorizationError`: Permission-related errors
  - `RateLimitError`: Rate limiting violations

### Error Metadata
- Timestamp tracking
- Agent identification
- Conversation tracking
- Severity levels
- Error categorization
- Retry counting
- Stack trace capture
- Contextual information

### Error Response System
- Standardized error responses
- User-friendly message templates
- Error codes for tracking
- Detailed error metadata
- Configurable response formats

### Retry Mechanism
- Configurable retry policies:
  - Processing errors: 3 retries, 1s delay
  - Rate limit errors: 2 retries, 5s delay
  - Default: 1 retry, 1s delay
- Automatic retry handling
- Progressive retry counting
- Delay between attempts

### Error Logging
- Centralized error logging
- Log file: `logs/errors.log`
- Structured log format:
  - Timestamp
  - Error code
  - Error message
  - Full metadata
  - Stack traces

## Monitoring System

- Real-time metrics collection
- System health monitoring
- Agent performance tracking
- Alert management
- Visualization endpoints for metrics

## Content Filtering System (`content_filter.py`)

### Filter Rules
- Categories monitored:
  - Hate speech (severity: 5)
  - Violence (severity: 5)
  - Adult content (severity: 4)
  - Personal information (severity: 3)
  - Harmful topics (severity: 4)
  - Profanity (severity: 2)
  - Spam (severity: 1)

### Filtering Features
- Pattern-based detection using regex
- Context-aware filtering
- Multi-language support
- Configurable severity levels
- Content replacement with asterisks

### Safety Checks
- Real-time content analysis
- Conversation context examination
- Severity threshold enforcement
- Detailed match reporting
- Filtered content generation

### Configuration
- Rules loaded from: `config/filter_rules.json`
- Default rules fallback
- Customizable patterns and context words
- Language-specific rule application
- Adjustable severity thresholds

This architecture ensures efficient handling of hotel guest requests using a local LLM model, with proper coordination between specialized agents, robust error handling, and comprehensive content safety measures.