"""
Room Service Agent for the Hotel AI Assistant.

This agent handles room service requests, such as requests for towels,
pillows, and other amenities.
"""

import logging
import os
from typing import Dict, List, Any, Optional, Type
from datetime import datetime, timedelta
import uuid

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from langchain_huggingface import HuggingFacePipeline

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
            name="room_service_agent"
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
        
        # Format the prompt first
        formatted_prompt = self.prompt.format(input=formatted_input)
        
        # Then invoke the LLM with the formatted prompt
        llm_response = await self.llm.ainvoke(formatted_prompt)
        
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