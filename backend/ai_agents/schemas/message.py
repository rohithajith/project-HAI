"""
Message schema for the Hotel AI system.

This module defines the schema for messages in the Hotel AI system.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field

class Message(BaseModel):
    """Schema for a message in the Hotel AI system."""
    
    sender: Literal["user", "system", "agent"] = "user"
    content: str
    timestamp: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        
        schema_extra = {
            "example": {
                "sender": "user",
                "content": "What time is check-in?",
                "timestamp": "2023-01-01T12:00:00Z"
            }
        }