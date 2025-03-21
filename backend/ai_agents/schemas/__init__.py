"""
Schema package for the Hotel AI Assistant multi-agent system.

This package contains Pydantic models for agent communication and data validation.
"""

from .base import AgentMessage, AgentInput, AgentOutput, ConversationState
from .agent_schemas import (
    CheckInInput, CheckInOutput,
    RoomServiceInput, RoomServiceOutput,
    WellnessInput, WellnessOutput,
    EntertainmentInput, EntertainmentOutput,
    CabBookingInput, CabBookingOutput,
    ExtendStayInput, ExtendStayOutput
)

__all__ = [
    'AgentMessage',
    'AgentInput',
    'AgentOutput',
    'ConversationState',
    'CheckInInput',
    'CheckInOutput',
    'RoomServiceInput',
    'RoomServiceOutput',
    'WellnessInput',
    'WellnessOutput',
    'EntertainmentInput',
    'EntertainmentOutput',
    'CabBookingInput',
    'CabBookingOutput',
    'ExtendStayInput',
    'ExtendStayOutput'
]