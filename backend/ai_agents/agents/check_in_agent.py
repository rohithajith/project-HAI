"""
Check-in Agent for the Hotel AI Assistant.

This agent handles guest check-ins, verifying ID and payment information,
and updating the booking system.
"""

import logging
from typing import Dict, List, Any, Optional, Type
from datetime import datetime

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..schemas import AgentInput, AgentOutput, CheckInInput, CheckInOutput
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class CheckInAgent(BaseAgent):
    """Agent for handling guest check-ins."""
    
    def __init__(self, model_name: str = "gpt-4o"):
        """Initialize the Check-in Agent.
        
        Args:
            model_name: The name of the language model to use
        """
        super().__init__(
            name="check_in_agent",
            description="Handles guest check-ins, verifies ID and payment, and updates booking records"
        )
        
        # Initialize the language model
        self.llm = ChatOpenAI(model=model_name)
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a hotel check-in assistant. Your job is to help guests check in to the hotel.
            You need to verify their identity, confirm their booking details, and issue room keys.
            
            Follow these steps for check-in:
            1. Verify the guest's identity using their ID
            2. Confirm their booking details (dates, room type, etc.)
            3. Verify payment information
            4. Assign a room and issue a key
            5. Provide information about hotel amenities and services
            
            Be professional, courteous, and efficient. If there are any issues with the booking,
            try to resolve them or escalate to a human staff member if necessary.
            """),
            ("human", "{input}")
        ])
    
    @property
    def input_schema(self) -> Type[AgentInput]:
        """Get the input schema for this agent."""
        return CheckInInput
    
    @property
    def output_schema(self) -> Type[AgentOutput]:
        """Get the output schema for this agent."""
        return CheckInOutput
    
    async def process(self, input_data: CheckInInput) -> CheckInOutput:
        """Process a check-in request.
        
        Args:
            input_data: The check-in request data
            
        Returns:
            The result of the check-in process
        """
        logger.info(f"Processing check-in for booking ID: {input_data.booking_id}")
        
        # Extract the latest user message
        latest_message = input_data.messages[-1].content if input_data.messages else ""
        
        # Prepare context for the LLM
        context = {
            "booking_id": input_data.booking_id or "Unknown",
            "guest_name": input_data.guest_name or "Unknown",
            "id_verified": "Yes" if input_data.id_verification else "No",
            "payment_verified": "Yes" if input_data.payment_verification else "No",
            "conversation_history": "\n".join([f"{m.sender}: {m.content}" for m in input_data.messages[:-1]]),
            "latest_message": latest_message
        }
        
        # Format the input for the LLM
        formatted_input = f"""
        Booking ID: {context['booking_id']}
        Guest Name: {context['guest_name']}
        ID Verified: {context['id_verified']}
        Payment Verified: {context['payment_verified']}
        
        Conversation History:
        {context['conversation_history']}
        
        Latest Message:
        {context['latest_message']}
        """
        
        # Get a response from the LLM
        llm_response = await self.llm.ainvoke(
            self.prompt.format(input=formatted_input)
        )
        
        # Extract booking details and check-in status from the response
        # In a real implementation, this would interact with a database
        # For now, we'll simulate this with some logic
        
        # Simulate checking the booking system
        booking_details = await self._get_booking_details(input_data.booking_id)
        
        # Determine check-in status based on verification flags
        check_in_status = "completed" if input_data.id_verification and input_data.payment_verification else "pending"
        
        # Assign a room number (in a real system, this would be from the booking system)
        room_number = "301" if check_in_status == "completed" else None
        
        # Create the response message
        response_message = self.create_message(
            content=llm_response.content,
            recipient="user"
        )
        
        # Create and return the output
        return CheckInOutput(
            messages=[response_message],
            actions=[{"type": "update_booking", "booking_id": input_data.booking_id, "status": "checked_in"}] if check_in_status == "completed" else [],
            status=check_in_status,
            booking_details=booking_details,
            check_in_status=check_in_status,
            room_number=room_number,
            key_issued=check_in_status == "completed"
        )
    
    async def _get_booking_details(self, booking_id: Optional[str]) -> Dict[str, Any]:
        """Get booking details from the booking system.
        
        In a real implementation, this would query a database.
        For now, we'll return mock data.
        
        Args:
            booking_id: The ID of the booking to retrieve
            
        Returns:
            The booking details
        """
        # Mock booking details
        return {
            "booking_id": booking_id or "BK12345",
            "guest_name": "John Doe",
            "check_in_date": datetime.now().strftime("%Y-%m-%d"),
            "check_out_date": datetime.now().strftime("%Y-%m-%d"),
            "room_type": "Deluxe",
            "number_of_guests": 2,
            "special_requests": "None"
        }