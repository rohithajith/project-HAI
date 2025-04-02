from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from .base_agent import BaseAgent, AgentOutput, ToolDefinition, ToolParameters, ToolParameterProperty

class GuestIdentification(BaseModel):
    """Schema for guest identification data."""
    id_type: str = Field(..., description="Type of ID (passport, driver's license, etc)")
    id_number: str = Field(..., description="ID document number")
    full_name: str = Field(..., description="Guest's full name")
    email: EmailStr = Field(..., description="Guest's email address")
    date_of_birth: datetime = Field(..., description="Guest's date of birth")

class PaymentInfo(BaseModel):
    """Schema for payment verification."""
    payment_method: str = Field(..., description="Method of payment")
    payment_status: str = Field(..., description="Status of payment")
    amount_paid: float = Field(..., description="Amount paid")
    transaction_id: str = Field(..., description="Payment transaction ID")

class CheckInAgent(BaseAgent):
    """Agent responsible for handling guest check-ins."""
    
    def __init__(self):
        self.name = "check_in_agent"
        self.priority = 10  # High priority for check-in requests
        
        # Define tools available to this agent
        self.tools = [
            ToolDefinition(
                name="verify_id",
                description="Verify guest identification documents",
                parameters=ToolParameters(
                    type="object",
                    properties={
                        "id_type": ToolParameterProperty(
                            type="string",
                            description="Type of ID document",
                            enum=["passport", "driver_license", "national_id"]
                        ),
                        "id_number": ToolParameterProperty(
                            type="string",
                            description="ID document number"
                        )
                    },
                    required=["id_type", "id_number"]
                )
            ),
            ToolDefinition(
                name="verify_payment",
                description="Verify payment status for check-in",
                parameters=ToolParameters(
                    type="object",
                    properties={
                        "booking_id": ToolParameterProperty(
                            type="string",
                            description="Booking reference number"
                        )
                    },
                    required=["booking_id"]
                )
            )
        ]

    def should_handle(self, message: str, history: List[Dict[str, Any]]) -> bool:
        """Determine if this agent should handle the message."""
        check_in_keywords = [
            "check in", "check-in", "checking in",
            "arrive", "arrival", "register",
            "room key", "book", "booking",
            "reservation"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in check_in_keywords)

    async def process(self, message: str, history: List[Dict[str, Any]]) -> AgentOutput:
        """Process check-in related requests."""
        # GDPR compliance: Ensure sensitive data handling
        if self._contains_sensitive_data(message):
            return AgentOutput(
                response="For your privacy and security, please do not share sensitive personal "
                        "information in the chat. Our secure check-in system will prompt you "
                        "for necessary information at the appropriate time."
            )

        # Content filtering
        if self._contains_harmful_content(message):
            return AgentOutput(
                response="I apologize, but I cannot process messages containing inappropriate "
                        "or harmful content. How else may I assist you with your check-in?"
            )

        # Extract booking reference if available
        booking_ref = self._extract_booking_reference(message, history)
        
        if booking_ref:
            # Verify booking and payment
            return await self._handle_existing_booking(booking_ref)
        else:
            # Guide user through check-in process
            return await self._guide_checkin_process(message, history)

    def _contains_sensitive_data(self, message: str) -> bool:
        """Check if message contains sensitive personal data."""
        sensitive_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
            r'\b\d{16}\b',  # Credit card number pattern
            r'\b(?:\d[ -]*?){13,16}\b'  # Various card number formats
        ]
        import re
        return any(re.search(pattern, message) for pattern in sensitive_patterns)

    def _contains_harmful_content(self, message: str) -> bool:
        """Check for harmful or inappropriate content."""
        harmful_keywords = [
            "lgbtq", "rape", "bomb", "terror", "politics",
            "weapon", "drugs", "explicit", "offensive"
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in harmful_keywords)

    def _extract_booking_reference(self, message: str, history: List[Dict[str, Any]]) -> Optional[str]:
        """Extract booking reference from message or history."""
        import re
        # Look for common booking reference patterns
        patterns = [
            r'booking[:\s]*([A-Z0-9]{6,})',
            r'reservation[:\s]*([A-Z0-9]{6,})',
            r'reference[:\s]*([A-Z0-9]{6,})'
        ]
        
        # Check current message first
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Check history if not found in current message
        for entry in reversed(history):
            content = entry.get('content', '')
            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        return None

    async def _handle_existing_booking(self, booking_ref: str) -> AgentOutput:
        """Handle check-in for existing booking."""
        return AgentOutput(
            response=f"I've found your booking reference {booking_ref}. "
                    "To protect your privacy, please proceed to our secure check-in "
                    "terminal or speak with our front desk staff to complete your "
                    "check-in process. They will verify your ID and finalize the "
                    "payment details securely.",
            notifications=[{
                "type": "booking_verification",
                "booking_ref": booking_ref
            }]
        )

    async def _guide_checkin_process(self, message: str, history: List[Dict[str, Any]]) -> AgentOutput:
        """Guide user through initial check-in process."""
        return AgentOutput(
            response="Welcome! To begin the check-in process, please have your "
                    "booking reference number ready. If you have a booking, "
                    "please share your booking reference. If you need to make "
                    "a new booking, I can help you with that as well. What "
                    "would you like to do?",
            notifications=[{
                "type": "checkin_started",
                "timestamp": datetime.utcnow().isoformat()
            }]
        )