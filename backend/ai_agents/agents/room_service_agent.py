"""
Room Service Agent for the Hotel AI Assistant.

This agent handles room service requests, such as requests for towels,
pillows, and other amenities.
"""

import logging
from typing import Dict, List, Any, Optional, Type
from datetime import datetime, timedelta
import uuid

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..schemas import AgentInput, AgentOutput, RoomServiceInput, RoomServiceOutput
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class RoomServiceAgent(BaseAgent):
    """Agent for handling room service requests."""
    
    def __init__(self, model_name: str = "gpt-4o"):
        """Initialize the Room Service Agent.
        
        Args:
            model_name: The name of the language model to use
        """
        super().__init__(
            name="room_service_agent",
            description="Handles room service requests for towels, pillows, and other amenities"
        )
        
        # Initialize the language model
        self.llm = ChatOpenAI(model=model_name)
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a hotel room service assistant. Your job is to help guests with room service requests.
            You can handle requests for items like towels, pillows, toiletries, and other amenities.
            
            Follow these steps for room service requests:
            1. Identify the specific items requested
            2. Confirm the quantity needed
            3. Note any special instructions
            4. Provide an estimated delivery time
            5. Create a service request in the system
            
            Be professional, courteous, and efficient. If the guest requests something that's not available,
            suggest alternatives or explain why it's not available.
            """),
            ("human", "{input}")
        ])
        
        # Available items and their status
        self.available_items = {
            "towels": True,
            "pillows": True,
            "blankets": True,
            "toiletries": True,
            "water bottles": True,
            "coffee": True,
            "tea": True,
            "sugar": True,
            "ice": True
        }
    
    @property
    def input_schema(self) -> Type[AgentInput]:
        """Get the input schema for this agent."""
        return RoomServiceInput
    
    @property
    def output_schema(self) -> Type[AgentOutput]:
        """Get the output schema for this agent."""
        return RoomServiceOutput
    
    async def process(self, input_data: RoomServiceInput) -> RoomServiceOutput:
        """Process a room service request.
        
        Args:
            input_data: The room service request data
            
        Returns:
            The result of the room service request
        """
        logger.info(f"Processing room service request for room: {input_data.room_number}")
        
        # Extract the latest user message
        latest_message = input_data.messages[-1].content if input_data.messages else ""
        
        # Prepare context for the LLM
        context = {
            "room_number": input_data.room_number or "Unknown",
            "request_type": input_data.request_type or "Unknown",
            "quantity": input_data.quantity or 1,
            "special_instructions": input_data.special_instructions or "None",
            "conversation_history": "\n".join([f"{m.sender}: {m.content}" for m in input_data.messages[:-1]]),
            "latest_message": latest_message
        }
        
        # Format the input for the LLM
        formatted_input = f"""
        Room Number: {context['room_number']}
        Request Type: {context['request_type']}
        Quantity: {context['quantity']}
        Special Instructions: {context['special_instructions']}
        
        Conversation History:
        {context['conversation_history']}
        
        Latest Message:
        {context['latest_message']}
        
        Available Items: {', '.join(item for item, available in self.available_items.items() if available)}
        """
        
        # Get a response from the LLM
        llm_response = await self.llm.ainvoke(
            self.prompt.format(input=formatted_input)
        )
        
        # Generate a request ID
        request_id = f"RS-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate estimated delivery time (15-30 minutes from now)
        current_time = datetime.now()
        estimated_delivery_time = current_time + timedelta(minutes=15 + (hash(request_id) % 15))
        
        # Determine if the requested item is available
        item_available = True
        if input_data.request_type and input_data.request_type.lower() in self.available_items:
            item_available = self.available_items[input_data.request_type.lower()]
        
        # Determine status based on availability
        status = "processing" if item_available else "unavailable"
        
        # Assign a staff member (in a real system, this would be from a staff management system)
        assigned_staff = "Alex Johnson" if status == "processing" else None
        
        # Create the response message
        response_message = self.create_message(
            content=llm_response.content,
            recipient="user"
        )
        
        # Create actions based on the request
        actions = []
        if status == "processing":
            actions.append({
                "type": "create_service_request",
                "request_id": request_id,
                "room_number": input_data.room_number,
                "request_type": input_data.request_type,
                "quantity": input_data.quantity,
                "special_instructions": input_data.special_instructions,
                "assigned_staff": assigned_staff,
                "estimated_delivery_time": estimated_delivery_time.isoformat()
            })
        
        # Create and return the output
        return RoomServiceOutput(
            messages=[response_message],
            actions=actions,
            status=status,
            request_id=request_id,
            estimated_delivery_time=estimated_delivery_time if status == "processing" else None,
            assigned_staff=assigned_staff
        )
    
    async def update_item_availability(self, item: str, available: bool) -> None:
        """Update the availability of an item.
        
        Args:
            item: The item to update
            available: Whether the item is available
        """
        if item.lower() in self.available_items:
            self.available_items[item.lower()] = available
            logger.info(f"Updated availability of {item}: {available}")