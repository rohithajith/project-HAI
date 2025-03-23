
"""
Check-in Agent for the Hotel AI Assistant.

This agent handles guest check-ins, verifying ID and payment information,
and updating the booking system.
"""

import logging
import os
from typing import Dict, List, Any, Optional, Type
from datetime import datetime

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from langchain_huggingface import HuggingFacePipeline

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
            name="check_in_agent"
        )
        
        # Always use the local quantized model
        model, tokenizer = self.load_model()
        
        # Create a text generation pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=2000,
            temperature=0.7,
            top_p=0.9,
            top_k=50,
            repetition_penalty=1.2
        )
        
        # Create a LangChain wrapper around the pipeline
        self.llm = HuggingFacePipeline(pipeline=pipe)
        logger.info("✅ Using local quantized model")
        
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
    
    def load_model(self):
        """Load the local model from the correct snapshot directory"""
        # Get the root directory of the project (three levels up from the current script)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        model_path = os.path.join(project_root, "finetunedmodel-merged")
        
        logger.info(f"Loading model from: {model_path}")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True,
            local_files_only=True  # Explicitly use local files only
        )
        
        # Configure 8-bit quantization (force GPU only)
        quantization_config = BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_enable_fp32_cpu_offload=False  # Disable CPU offload
        )
        
        # Load model with 8-bit quantization on GPU only
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            trust_remote_code=True,
            local_files_only=True,  # Explicitly use local files only
            device_map="cuda:0",  # Force GPU only
            quantization_config=quantization_config,  # Use 8-bit quantization
            low_cpu_mem_usage=True  # Optimize for low CPU memory usage
        )
        
        logger.info("✅ Model loaded successfully!")
        return model, tokenizer
    
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
        
        # Format the prompt first
        formatted_prompt = self.prompt.format(input=formatted_input)
        
        # Then invoke the LLM with the formatted prompt
        llm_response = await self.llm.ainvoke(formatted_prompt)
        
        # Extract booking details and check-in status from the response
        # In a real implementation, this would interact with a database
        # For now, we'll simulate this with some logic
        
        # Simulate checking the booking system
        booking_details = await self._get_booking_details(input_data.booking_id)
        
        # Determine check-in status based on verification flags
        check_in_status = "completed" if input_data.id_verification and input_data.payment_verification else "pending"
        
        # Assign a room number (in a real system, this would be from the booking system)
        room_number = "301" if check_in_status == "completed" else None
        
        # Handle the response which might be a string or an object with a content attribute
        if hasattr(llm_response, 'content'):
            response_content = llm_response.content
        else:
            response_content = llm_response
        
        # Create the response message
        response_message = self.create_message(
            content=response_content,
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