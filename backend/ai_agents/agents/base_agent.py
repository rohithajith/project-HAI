"""
Base agent class for the Hotel AI Assistant multi-agent system.

This module defines the BaseAgent class that provides common functionality
for all specialized agents in the system.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Type
from datetime import datetime
import uuid

from ..schemas import AgentMessage, AgentInput, AgentOutput

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents in the Hotel AI Assistant system."""
    
    def __init__(self, name: str, description: str):
        """Initialize the agent with a name and description.
        
        Args:
            name: The name of the agent
            description: A description of the agent's purpose and capabilities
        """
        self.name = name
        self.description = description
        self.tools = []
        self.memory = {}
        logger.info(f"Initialized agent: {name}")
    
    @property
    @abstractmethod
    def input_schema(self) -> Type[AgentInput]:
        """Get the input schema for this agent."""
        pass
    
    @property
    @abstractmethod
    def output_schema(self) -> Type[AgentOutput]:
        """Get the output schema for this agent."""
        pass
    
    @abstractmethod
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process an input and generate an output.
        
        This is the main method that specialized agents must implement.
        
        Args:
            input_data: The input data for the agent to process
            
        Returns:
            The output data from the agent's processing
        """
        pass
    
    def create_message(self, content: str, recipient: str = "user") -> AgentMessage:
        """Create a new message from this agent.
        
        Args:
            content: The content of the message
            recipient: The recipient of the message (default: "user")
            
        Returns:
            A new AgentMessage
        """
        return AgentMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            sender=self.name,
            recipient=recipient,
            content=content,
            metadata={}
        )
    
    def add_tool(self, tool: Any) -> None:
        """Add a tool to the agent's toolkit.
        
        Args:
            tool: The tool to add
        """
        self.tools.append(tool)
        logger.info(f"Added tool to agent {self.name}: {tool.__name__ if hasattr(tool, '__name__') else str(tool)}")
    
    def remember(self, key: str, value: Any) -> None:
        """Store a value in the agent's memory.
        
        Args:
            key: The key to store the value under
            value: The value to store
        """
        self.memory[key] = value
    
    def recall(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the agent's memory.
        
        Args:
            key: The key to retrieve
            default: The default value to return if the key is not found
            
        Returns:
            The value stored under the key, or the default value if not found
        """
        return self.memory.get(key, default)
    
    def __str__(self) -> str:
        """Get a string representation of the agent."""
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        """Get a string representation of the agent for debugging."""
        return f"<{self.__class__.__name__} name='{self.name}'>"