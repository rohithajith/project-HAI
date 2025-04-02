from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type
from pydantic import BaseModel, Field
from datetime import datetime
import re
from .content_filter import content_filter, FilterResult

class ToolParameterProperty(BaseModel):
    """Defines a single parameter property for a tool."""
    type: str
    description: Optional[str] = None
    enum: Optional[List[str]] = None
    default: Optional[Any] = None

class ToolParameters(BaseModel):
    """Defines the parameters structure for a tool."""
    type: str = "object"
    properties: Dict[str, ToolParameterProperty]
    required: Optional[List[str]] = None

class ToolDefinition(BaseModel):
    """Defines the structure of a tool available to an agent."""
    name: str
    description: str
    parameters: ToolParameters

class AgentOutput(BaseModel):
    """Standard output structure for an agent's processing step."""
    response: str
    notifications: List[Dict[str, Any]] = Field(default_factory=list)
    tool_used: bool = False
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    filter_result: Optional[FilterResult] = None

class BaseAgent(ABC):
    """Abstract base class for all AI agents."""
    name: str = "BaseAgent"
    priority: int = 0  # Higher number means higher priority
    tools: List[ToolDefinition] = []
    
    def __init__(self):
        """Initialize the agent with default settings."""
        self.max_severity_threshold = 3  # Default maximum allowed severity
        self.language = "en"  # Default language
        
    @abstractmethod
    def should_handle(self, message: str, history: List[Dict[str, Any]]) -> bool:
        """
        Determine if this agent is appropriate to handle the given message.

        Args:
            message: The user's current message.
            history: The conversation history.

        Returns:
            True if the agent should handle the message, False otherwise.
        """
        pass

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Return the tool definitions in a format suitable for LangGraph's create_react_agent.
        Converts ToolDefinition objects to the expected LangGraph tool format.
        """
        formatted_tools = []
        for tool in self.tools:
            formatted_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": tool.parameters.type,
                        "properties": {
                            name: prop.model_dump(exclude_none=True)
                            for name, prop in tool.parameters.properties.items()
                        }
                    }
                }
            }
            if tool.parameters.required:
                formatted_tool["function"]["parameters"]["required"] = tool.parameters.required
            formatted_tools.append(formatted_tool)
        return formatted_tools

    @abstractmethod
    async def process(self, message: str, history: List[Dict[str, Any]]) -> AgentOutput:
        """
        Process the message using the agent's logic and tools.

        Args:
            message: The user's current message.
            history: The conversation history.

        Returns:
            An AgentOutput object containing the response and related information.
        """
        pass

    def check_content_safety(self, 
                           message: str, 
                           history: Optional[List[Dict[str, Any]]] = None) -> FilterResult:
        """
        Check if content is safe using the content filter.

        Args:
            message: The content to check
            history: Optional conversation history for context

        Returns:
            FilterResult containing the analysis details
        """
        return content_filter.check_content(
            content=message,
            language=self.language,
            context=history
        )

    def is_content_safe(self, 
                       message: str, 
                       history: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        Check if content is safe (below maximum severity threshold).

        Args:
            message: The content to check
            history: Optional conversation history for context

        Returns:
            True if content is safe, False otherwise
        """
        return content_filter.is_content_safe(
            content=message,
            language=self.language,
            context=history,
            max_severity=self.max_severity_threshold
        )

    def filter_harmful_content(self, 
                             message: str, 
                             history: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Filter out harmful content from the message.

        Args:
            message: The content to filter
            history: Optional conversation history for context

        Returns:
            Filtered content with harmful parts replaced by asterisks
        """
        return content_filter.filter_harmful_content(
            content=message,
            language=self.language,
            context=history
        )

    def create_safety_violation_response(self, filter_result: FilterResult) -> AgentOutput:
        """
        Create a standardized response for content safety violations.

        Args:
            filter_result: The FilterResult from content checking

        Returns:
            AgentOutput with appropriate response and notifications
        """
        category_messages = {
            "hate_speech": "discriminatory or hateful content",
            "violence": "violent or threatening content",
            "adult_content": "explicit or inappropriate content",
            "personal_info": "sensitive personal information",
            "harmful_topics": "harmful or controversial topics",
            "profanity": "inappropriate language",
            "spam": "promotional or spam content"
        }
        
        # Create specific message based on violated categories
        violation_details = [
            category_messages.get(category, "inappropriate content")
            for category in filter_result.categories
        ]
        
        response = (
            "I apologize, but I cannot process messages containing "
            f"{', '.join(violation_details)}. Please rephrase your request "
            "appropriately, and I'll be happy to assist you."
        )
        
        return AgentOutput(
            response=response,
            notifications=[{
                "type": "content_violation",
                "severity": filter_result.severity,
                "categories": filter_result.categories,
                "timestamp": datetime.utcnow().isoformat()
            }],
            filter_result=filter_result
        )

    def _extract_room_number(self, history: List[Dict[str, Any]]) -> Optional[str]:
        """
        Extracts room number from conversation history.
        
        Args:
            history: The conversation history to search
            
        Returns:
            Room number if found, None otherwise
        """
        for entry in reversed(history):  # Check recent messages first
            if entry.get('role') == 'user' or entry.get('type') == 'human':
                content = entry.get('content', '')
                # More robust regex to handle variations like "room 101", "room number 101", "room:101"
                match = re.search(r'room(?: number)?\s*:?\s*(\d+)', content, re.IGNORECASE)
                if match:
                    return match.group(1)
        return None

    def _extract_booking_reference(self, 
                                 message: str, 
                                 history: List[Dict[str, Any]]) -> Optional[str]:
        """
        Extract booking reference from message or history.
        
        Args:
            message: Current message to check
            history: Conversation history to search
            
        Returns:
            Booking reference if found, None otherwise
        """
        patterns = [
            r'booking[:\s]*([A-Z0-9]{6,})',
            r'reservation[:\s]*([A-Z0-9]{6,})',
            r'reference[:\s]*([A-Z0-9]{6,})'
        ]
        
        # Check current message first
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Check history if not found in current message
        for entry in reversed(history):
            content = entry.get('content', '')
            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        return None

    def _is_in_conversation(self, 
                          history: List[Dict[str, Any]], 
                          lookback: int = 3) -> bool:
        """
        Check if we're in an ongoing conversation with this agent.
        
        Args:
            history: Conversation history to check
            lookback: Number of messages to check (default: 3)
            
        Returns:
            True if in conversation with this agent, False otherwise
        """
        if not history:
            return False
            
        recent_history = history[-lookback:]  # Look at last few messages
        for entry in recent_history:
            if entry.get('agent') == self.name:
                return True
        return False
        
    async def handle_tool_call(self, tool_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a tool call by executing the appropriate tool logic.
        
        Args:
            tool_name: Name of the tool to execute
            inputs: Tool input parameters
            
        Returns:
            Tool execution results
        """
        # Find the tool definition
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
            
        # Validate inputs against tool parameters
        required = tool.parameters.required or []
        for param in required:
            if param not in inputs:
                raise ValueError(f"Missing required parameter: {param}")
                
        # Execute tool-specific logic
        if tool_name == "check_menu_availability":
            # Example implementation
            return {
                "available": True,
                "estimated_wait": "15 minutes"
            }
        elif tool_name == "place_order":
            # Example implementation
            return {
                "order_id": "ORD123",
                "status": "confirmed",
                "estimated_delivery": "30 minutes"
            }
        else:
            raise NotImplementedError(f"Tool {tool_name} not implemented")