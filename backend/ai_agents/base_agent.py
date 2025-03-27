from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type
from pydantic import BaseModel, Field

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

class BaseAgent(ABC):
    """Abstract base class for all AI agents."""
    name: str = "BaseAgent"
    priority: int = 0 # Higher number means higher priority
    tools: List[ToolDefinition] = []

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
        Return the tool definitions in a format suitable for LLMs (e.g., OpenAI functions).
        Converts Pydantic models to dictionaries.
        """
        return [tool.model_dump(exclude_none=True) for tool in self.tools]

    @abstractmethod
    async def process(self, message: str, history: List[Dict[str, Any]]) -> AgentOutput:
        """
        Process the message using the agent's logic and tools.

        Args:
            message: The user's current message.
            history: The conversation history.

        Returns:
            An AgentOutput object containing the response, notifications, and tool usage info.
        """
        pass

    # Helper method often needed by agents
    def _extract_room_number(self, history: List[Dict[str, Any]]) -> Optional[str]:
        """Extracts room number from conversation history (example helper)."""
        import re
        for entry in reversed(history): # Check recent messages first
            if entry.get('role') == 'user' or entry.get('type') == 'human':
                content = entry.get('content', '')
                # More robust regex to handle variations like "room 101", "room number 101", "room:101"
                match = re.search(r'room(?: number)?\s*:?\s*(\d+)', content, re.IGNORECASE)
                if match:
                    return match.group(1)
        return None