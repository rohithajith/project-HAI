from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, time
from .base_agent import BaseAgent, AgentOutput, ToolDefinition, ToolParameters, ToolParameterProperty

class BookingResource(BaseModel):
    """Schema for bookable resources."""
    resource_id: str = Field(..., description="Unique identifier for the resource")
    resource_type: str = Field(..., description="Type of resource (meeting_room, coworking)")
    capacity: int = Field(..., description="Maximum capacity")
    amenities: List[str] = Field(..., description="Available amenities")
    hourly_rate: float = Field(..., description="Cost per hour")

class BookingRequest(BaseModel):
    """Schema for booking requests."""
    resource_type: str = Field(..., description="Type of resource needed")
    start_time: datetime = Field(..., description="Start time of booking")
    end_time: datetime = Field(..., description="End time of booking")
    attendees: int = Field(..., description="Number of attendees")
    required_amenities: Optional[List[str]] = Field(None, description="Required amenities")
    room_number: Optional[str] = Field(None, description="Guest's room number if applicable")

class ServicesBookingAgent(BaseAgent):
    """Agent responsible for handling meeting room and co-working space bookings."""
    
    def __init__(self):
        self.name = "services_booking_agent"
        self.priority = 6  # Medium priority for booking services
        
        # Define available tools
        self.tools = [
            ToolDefinition(
                name="check_resource_availability",
                description="Check availability of meeting rooms or co-working spaces",
                parameters=ToolParameters(
                    type="object",
                    properties={
                        "resource_type": ToolParameterProperty(
                            type="string",
                            description="Type of resource",
                            enum=["meeting_room", "coworking_space"]
                        ),
                        "start_time": ToolParameterProperty(
                            type="string",
                            description="Start time"
                        ),
                        "end_time": ToolParameterProperty(
                            type="string",
                            description="End time"
                        ),
                        "capacity": ToolParameterProperty(
                            type="integer",
                            description="Required capacity"
                        )
                    },
                    required=["resource_type", "start_time", "end_time"]
                )
            ),
            ToolDefinition(
                name="create_booking",
                description="Create a new resource booking",
                parameters=ToolParameters(
                    type="object",
                    properties={
                        "resource_id": ToolParameterProperty(
                            type="string",
                            description="ID of the resource to book"
                        ),
                        "start_time": ToolParameterProperty(
                            type="string",
                            description="Start time"
                        ),
                        "end_time": ToolParameterProperty(
                            type="string",
                            description="End time"
                        ),
                        "room_number": ToolParameterProperty(
                            type="string",
                            description="Guest room number"
                        )
                    },
                    required=["resource_id", "start_time", "end_time"]
                )
            ),
            ToolDefinition(
                name="modify_booking",
                description="Modify an existing booking",
                parameters=ToolParameters(
                    type="object",
                    properties={
                        "booking_id": ToolParameterProperty(
                            type="string",
                            description="Booking ID to modify"
                        ),
                        "start_time": ToolParameterProperty(
                            type="string",
                            description="New start time"
                        ),
                        "end_time": ToolParameterProperty(
                            type="string",
                            description="New end time"
                        )
                    },
                    required=["booking_id"]
                )
            )
        ]

    def should_handle(self, message: str, history: List[Dict[str, Any]]) -> bool:
        """Determine if this agent should handle the message."""
        booking_keywords = [
            "meeting room", "conference room", "co-working", "coworking",
            "workspace", "book a room", "reserve", "meeting space",
            "business center", "office space", "work area"
        ]
        
        message_lower = message.lower()
        
        # Check for booking keywords
        has_keywords = any(keyword in message_lower for keyword in booking_keywords)
        
        # Check if we're in an ongoing booking conversation
        in_conversation = self._is_in_booking_conversation(history)
        
        return has_keywords or in_conversation

    async def process(self, message: str, history: List[Dict[str, Any]]) -> AgentOutput:
        """Process booking related requests."""
        # Content filtering
        if self._contains_harmful_content(message):
            return AgentOutput(
                response="I apologize, but I cannot process messages containing inappropriate "
                        "content. How else may I assist you with booking services?"
            )

        # Extract room number if available
        room_number = self._extract_room_number(history)

        # Determine request type and handle accordingly
        if self._is_availability_check(message):
            return await self._handle_availability_check(message)
        elif self._is_booking_request(message):
            return await self._handle_booking_request(message, room_number)
        elif self._is_modification_request(message):
            return await self._handle_modification_request(message, room_number)
        elif self._is_cancellation_request(message):
            return await self._handle_cancellation_request(message, room_number)
        else:
            return await self._handle_general_inquiry()

    def _contains_harmful_content(self, message: str) -> bool:
        """Check for harmful or inappropriate content."""
        harmful_keywords = [
            "lgbtq", "rape", "bomb", "terror", "politics",
            "weapon", "drugs", "explicit", "offensive"
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in harmful_keywords)

    def _is_in_booking_conversation(self, history: List[Dict[str, Any]]) -> bool:
        """Check if we're in an ongoing booking conversation."""
        if not history:
            return False
            
        recent_history = history[-3:]  # Look at last 3 messages
        for entry in recent_history:
            if entry.get('agent') == self.name:
                return True
        return False

    def _is_availability_check(self, message: str) -> bool:
        """Check if message is asking about availability."""
        check_keywords = ["available", "free", "when", "check", "open"]
        return any(keyword in message.lower() for keyword in check_keywords)

    def _is_booking_request(self, message: str) -> bool:
        """Check if message is a booking request."""
        book_keywords = ["book", "reserve", "schedule", "need a room"]
        return any(keyword in message.lower() for keyword in book_keywords)

    def _is_modification_request(self, message: str) -> bool:
        """Check if message is requesting to modify a booking."""
        mod_keywords = ["change", "modify", "reschedule", "update"]
        return any(keyword in message.lower() for keyword in mod_keywords)

    def _is_cancellation_request(self, message: str) -> bool:
        """Check if message is requesting to cancel a booking."""
        cancel_keywords = ["cancel", "remove", "delete"]
        return any(keyword in message.lower() for keyword in cancel_keywords)

    async def _handle_availability_check(self, message: str) -> AgentOutput:
        """Handle requests to check resource availability."""
        return AgentOutput(
            response="I can help you check availability. We have:\n\n"
                    "Meeting Rooms:\n"
                    "1. Executive Boardroom (up to 20 people)\n"
                    "2. Conference Room A (up to 12 people)\n"
                    "3. Conference Room B (up to 8 people)\n\n"
                    "Co-working Spaces:\n"
                    "1. Business Center (open workspace)\n"
                    "2. Private Pods (1-2 people)\n\n"
                    "Please let me know:\n"
                    "1. Which type of space you need\n"
                    "2. Number of people\n"
                    "3. Preferred date and time\n"
                    "4. Duration of booking",
            notifications=[{
                "type": "availability_inquiry",
                "timestamp": datetime.utcnow().isoformat()
            }]
        )

    async def _handle_booking_request(self, message: str, room_number: Optional[str]) -> AgentOutput:
        """Handle requests to make a booking."""
        if not room_number:
            return AgentOutput(
                response="To proceed with your booking, I'll need your room number. "
                        "Could you please provide it?"
            )

        return AgentOutput(
            response="I'll help you book a space. To ensure you get exactly what you need, "
                    "please confirm:\n\n"
                    "1. Type of space (meeting room/co-working)\n"
                    "2. Number of attendees\n"
                    "3. Date and time\n"
                    "4. Duration\n"
                    "5. Any required amenities (projector, whiteboard, etc.)\n\n"
                    "You can say something like 'I need a meeting room for 8 people "
                    "tomorrow at 2 PM for 2 hours with a projector.'",
            notifications=[{
                "type": "booking_initiated",
                "room_number": room_number,
                "timestamp": datetime.utcnow().isoformat()
            }]
        )

    async def _handle_modification_request(self, message: str, room_number: Optional[str]) -> AgentOutput:
        """Handle requests to modify an existing booking."""
        if not room_number:
            return AgentOutput(
                response="To modify your booking, I'll need your room number. "
                        "Could you please provide it?"
            )

        return AgentOutput(
            response="I can help you modify your booking. Please let me know:\n\n"
                    "1. Your booking reference number\n"
                    "2. What you'd like to change (time, duration, room type)\n\n"
                    "I'll check availability and help you make the changes.",
            notifications=[{
                "type": "modification_requested",
                "room_number": room_number,
                "timestamp": datetime.utcnow().isoformat()
            }]
        )

    async def _handle_cancellation_request(self, message: str, room_number: Optional[str]) -> AgentOutput:
        """Handle requests to cancel a booking."""
        if not room_number:
            return AgentOutput(
                response="To cancel your booking, I'll need your room number. "
                        "Could you please provide it?"
            )

        return AgentOutput(
            response="I can help you cancel your booking. Please note our cancellation policy:\n\n"
                    "- Free cancellation up to 24 hours before\n"
                    "- 50% charge for cancellations within 24 hours\n"
                    "- Full charge for no-shows\n\n"
                    "Please provide your booking reference number to proceed with cancellation.",
            notifications=[{
                "type": "cancellation_requested",
                "room_number": room_number,
                "timestamp": datetime.utcnow().isoformat()
            }]
        )

    async def _handle_general_inquiry(self) -> AgentOutput:
        """Handle general inquiries about booking services."""
        return AgentOutput(
            response="Welcome to our booking services! I can help you with:\n\n"
                    "1. Meeting Rooms & Conference Facilities\n"
                    "- Executive Boardroom (up to 20 people)\n"
                    "- Conference Rooms (8-12 people)\n"
                    "- All rooms equipped with AV equipment\n\n"
                    "2. Co-working Spaces\n"
                    "- Business Center (open workspace)\n"
                    "- Private Pods (1-2 people)\n"
                    "- High-speed internet & printing services\n\n"
                    "Would you like to:\n"
                    "1. Check availability?\n"
                    "2. Make a booking?\n"
                    "3. Modify an existing booking?\n"
                    "4. Learn more about our facilities?",
            notifications=[{
                "type": "general_booking_inquiry",
                "timestamp": datetime.utcnow().isoformat()
            }]
        )