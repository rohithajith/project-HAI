"""
Hotel AI Assistant multi-agent system.

This package implements a multi-agent system for a hotel assistant using LangGraph
for workflow management and Pydantic-AI for schema enforcement.
"""

__version__ = "0.1.0"
__all__ = [
    'GuestRequestAgent'
]

# Import GuestRequestAgent directly to avoid circular imports
from .guest_request_agent import GuestRequestAgent