"""
Base schemas for the Hotel AI Assistant multi-agent system.

This module defines the core schema classes used for agent communication,
including message formats, input/output structures, and common data types.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, TypedDict
from pydantic import BaseModel, Field


class AgentMessage(BaseModel):
    """Base schema for messages exchanged between agents."""
    
    id: str = Field(..., description="Unique identifier for the message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Time when the message was created")
    sender: str = Field(..., description="Identifier of the agent that sent the message")
    recipient: str = Field(..., description="Identifier of the agent that should receive the message")
    content: str = Field(..., description="Content of the message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the message")


class AgentInput(BaseModel):
    """Base schema for inputs to agents."""
    
    messages: List[AgentMessage] = Field(..., description="List of messages in the conversation")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context for the agent")


class AgentOutput(BaseModel):
    """Base schema for outputs from agents."""
    
    messages: List[AgentMessage] = Field(..., description="List of messages to add to the conversation")
    actions: List[Dict[str, Any]] = Field(default_factory=list, description="Actions to perform as a result of the agent's processing")
    status: str = Field(..., description="Status of the agent's processing (success, error, etc.)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the output")


class ConversationState(TypedDict):
    """State of a conversation in the LangGraph workflow."""
    
    messages: List[Dict[str, str]]
    current_agent: Optional[str]
    agent_outputs: Dict[str, Any]