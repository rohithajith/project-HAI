from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, time
from .base_agent import BaseAgent, AgentOutput, ToolDefinition, ToolParameters, ToolParameterProperty

class WellnessPreferences(BaseModel):
    """Schema for guest wellness preferences."""
    experience_level: str = Field(..., description="Beginner, Intermediate, or Advanced")
    preferred_time: Optional[time] = Field(None, description="Preferred time for sessions")
    health_conditions: Optional[List[str]] = Field(None, description="Any health conditions to consider")
    focus_areas: List[str] = Field(..., description="Areas of focus (e.g., stress, sleep, fitness)")

class WellnessBooking(BaseModel):
    """Schema for wellness service bookings."""
    service_type: str = Field(..., description="Type of wellness service")
    session_time: datetime = Field(..., description="Scheduled time for the service")
    duration: int = Field(..., description="Duration in minutes")
    room_number: str = Field(..., description="Guest's room number")
    special_requests: Optional[str] = Field(None, description="Any special requirements")

class WellnessAgent(BaseAgent):
    """Agent responsible for wellness services and guided experiences."""
    
    def __init__(self):
        self.name = "wellness_agent"
        self.priority = 7  # Medium priority for wellness services
        
        # Define available tools
        self.tools = [
            ToolDefinition(
                name="check_availability",
                description="Check availability for wellness services",
                parameters=ToolParameters(
                    type="object",
                    properties={
                        "service_type": ToolParameterProperty(
                            type="string",
                            description="Type of wellness service",
                            enum=["meditation", "yoga", "fitness", "spa"]
                        ),
                        "preferred_time": ToolParameterProperty(
                            type="string",
                            description="Preferred time slot"
                        )
                    },
                    required=["service_type"]
                )
            ),
            ToolDefinition(
                name="book_session",
                description="Book a wellness session",
                parameters=ToolParameters(
                    type="object",
                    properties={
                        "service_type": ToolParameterProperty(
                            type="string",
                            description="Type of wellness service"
                        ),
                        "session_time": ToolParameterProperty(
                            type="string",
                            description="Session time"
                        ),
                        "room_number": ToolParameterProperty(
                            type="string",
                            description="Guest room number"
                        )
                    },
                    required=["service_type", "session_time", "room_number"]
                )
            ),
            ToolDefinition(
                name="start_guided_session",
                description="Start a guided wellness session",
                parameters=ToolParameters(
                    type="object",
                    properties={
                        "session_type": ToolParameterProperty(
                            type="string",
                            description="Type of guided session"
                        ),
                        "duration": ToolParameterProperty(
                            type="integer",
                            description="Session duration in minutes"
                        ),
                        "level": ToolParameterProperty(
                            type="string",
                            description="Experience level"
                        )
                    },
                    required=["session_type", "duration"]
                )
            )
        ]

    def should_handle(self, message: str, history: List[Dict[str, Any]]) -> bool:
        """Determine if this agent should handle the message."""
        wellness_keywords = [
            "wellness", "meditation", "yoga", "fitness", "spa",
            "relax", "stress", "exercise", "mindfulness", "breathing",
            "massage", "workout", "health", "zen", "calm"
        ]
        
        message_lower = message.lower()
        
        # Check for wellness keywords
        has_keywords = any(keyword in message_lower for keyword in wellness_keywords)
        
        # Check if we're in an ongoing wellness conversation
        in_conversation = self._is_in_wellness_conversation(history)
        
        return has_keywords or in_conversation

    async def process(self, message: str, history: List[Dict[str, Any]]) -> AgentOutput:
        """Process wellness related requests."""
        # Content filtering
        if self._contains_harmful_content(message):
            return AgentOutput(
                response="I apologize, but I cannot process messages containing inappropriate "
                        "content. How else may I assist you with wellness services?"
            )

        # Extract room number for service bookings
        room_number = self._extract_room_number(history)

        # Determine request type and handle accordingly
        if self._is_meditation_request(message):
            return await self._handle_meditation_request(message, room_number)
        elif self._is_fitness_request(message):
            return await self._handle_fitness_request(message, room_number)
        elif self._is_spa_request(message):
            return await self._handle_spa_request(message, room_number)
        elif self._is_booking_status(message):
            return await self._handle_booking_status(room_number)
        else:
            return await self._handle_general_wellness_inquiry()

    def _contains_harmful_content(self, message: str) -> bool:
        """Check for harmful or inappropriate content."""
        harmful_keywords = [
            "lgbtq", "rape", "bomb", "terror", "politics",
            "weapon", "drugs", "explicit", "offensive"
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in harmful_keywords)

    def _is_in_wellness_conversation(self, history: List[Dict[str, Any]]) -> bool:
        """Check if we're in an ongoing wellness conversation."""
        if not history:
            return False
            
        recent_history = history[-3:]  # Look at last 3 messages
        for entry in recent_history:
            if entry.get('agent') == self.name:
                return True
        return False

    def _is_meditation_request(self, message: str) -> bool:
        """Check if the message is requesting meditation services."""
        meditation_keywords = ["meditation", "mindfulness", "breathing", "zen", "calm"]
        return any(keyword in message.lower() for keyword in meditation_keywords)

    def _is_fitness_request(self, message: str) -> bool:
        """Check if the message is requesting fitness services."""
        fitness_keywords = ["fitness", "workout", "exercise", "gym", "training"]
        return any(keyword in message.lower() for keyword in fitness_keywords)

    def _is_spa_request(self, message: str) -> bool:
        """Check if the message is requesting spa services."""
        spa_keywords = ["spa", "massage", "treatment", "facial", "therapy"]
        return any(keyword in message.lower() for keyword in spa_keywords)

    def _is_booking_status(self, message: str) -> bool:
        """Check if the message is requesting booking status."""
        status_keywords = ["status", "booking", "appointment", "scheduled", "reserved"]
        return any(keyword in message.lower() for keyword in status_keywords)

    async def _handle_meditation_request(self, message: str, room_number: Optional[str]) -> AgentOutput:
        """Handle meditation and mindfulness requests."""
        return AgentOutput(
            response="I can help you with guided meditation sessions. We offer:\n\n"
                    "1. Stress Relief Meditation (15 min)\n"
                    "2. Sleep Stories (20 min)\n"
                    "3. Mindful Breathing (10 min)\n"
                    "4. Body Scan Meditation (30 min)\n\n"
                    "Would you like me to start a guided session or book an in-person "
                    "meditation class with our wellness expert?",
            notifications=[{
                "type": "meditation_inquiry",
                "room_number": room_number,
                "timestamp": datetime.utcnow().isoformat()
            }]
        )

    async def _handle_fitness_request(self, message: str, room_number: Optional[str]) -> AgentOutput:
        """Handle fitness and exercise requests."""
        return AgentOutput(
            response="Our fitness services include:\n\n"
                    "1. Personal Training Sessions\n"
                    "2. Yoga Classes (All levels)\n"
                    "3. Virtual Workout Guide\n"
                    "4. Group Fitness Classes\n\n"
                    "Would you like to book a session or access our virtual fitness guide?",
            notifications=[{
                "type": "fitness_inquiry",
                "room_number": room_number,
                "timestamp": datetime.utcnow().isoformat()
            }]
        )

    async def _handle_spa_request(self, message: str, room_number: Optional[str]) -> AgentOutput:
        """Handle spa service requests."""
        return AgentOutput(
            response="Our spa offers the following services:\n\n"
                    "1. Swedish Massage (60/90 min)\n"
                    "2. Deep Tissue Massage (60/90 min)\n"
                    "3. Aromatherapy Treatment (60 min)\n"
                    "4. Facial Treatments (60 min)\n\n"
                    "Would you like to book a spa treatment? Please note that we recommend "
                    "booking at least 4 hours in advance.",
            notifications=[{
                "type": "spa_inquiry",
                "room_number": room_number,
                "timestamp": datetime.utcnow().isoformat()
            }]
        )

    async def _handle_booking_status(self, room_number: Optional[str]) -> AgentOutput:
        """Handle booking status inquiries."""
        if not room_number:
            return AgentOutput(
                response="To check your booking status, I'll need your room number. "
                        "Could you please provide it?"
            )
            
        return AgentOutput(
            response="Let me check the status of your wellness bookings...",
            notifications=[{
                "type": "booking_status_check",
                "room_number": room_number,
                "timestamp": datetime.utcnow().isoformat()
            }]
        )

    async def _handle_general_wellness_inquiry(self) -> AgentOutput:
        """Handle general wellness inquiries."""
        return AgentOutput(
            response="Welcome to our wellness services! I can help you with:\n\n"
                    "1. Guided Meditation & Mindfulness\n"
                    "2. Fitness & Exercise Programs\n"
                    "3. Spa Services & Treatments\n"
                    "4. Wellness Class Schedules\n\n"
                    "What type of wellness service are you interested in?",
            notifications=[{
                "type": "general_wellness_inquiry",
                "timestamp": datetime.utcnow().isoformat()
            }]
        )