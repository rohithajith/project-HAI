# ✅ Correct: only import from base and agent_schemas
from .base import AgentInput, AgentOutput, AgentMessage, ConversationState
from .agent_schemas import (
    CheckInInput, CheckInOutput,
    RoomServiceInput, RoomServiceOutput,
    WellnessInput, WellnessOutput,
    EntertainmentInput, EntertainmentOutput,
    CabBookingInput, CabBookingOutput,
    ExtendStayInput, ExtendStayOutput
)