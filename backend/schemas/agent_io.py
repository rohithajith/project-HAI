"""
Agent input/output schemas for the Hotel AI system.

This module defines the base schemas for agent inputs and outputs.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class AgentInput(BaseModel):
    """Base schema for agent inputs."""
    
    class Config:
        """Pydantic configuration."""
        
        extra = "allow"  # Allow extra fields

class AgentOutput(BaseModel):
    """Base schema for agent outputs."""
    
    class Config:
        """Pydantic configuration."""
        
        extra = "allow"  # Allow extra fields