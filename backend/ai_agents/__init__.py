
"""
Hotel AI Assistant multi-agent system.

This package implements a multi-agent system for a hotel assistant using LangGraph
for workflow management and Pydantic-AI for schema enforcement.
"""

from .supervisor import create_hotel_supervisor
from .agents import BaseAgent, CheckInAgent, RoomServiceAgent, WellnessAgent

__version__ = "0.1.0"
__all__ = [
    'create_hotel_supervisor',
    'BaseAgent',
    'CheckInAgent',
    'RoomServiceAgent',
    'WellnessAgent'
]