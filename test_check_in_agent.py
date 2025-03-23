"""
Standalone test script for the Hotel AI Assistant Check-in Agent.

This script tests the check-in agent functionality without relying on the package structure.
"""

import os
import sys
import asyncio
import torch
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline
# Use the updated import for HuggingFacePipeline
from langchain_huggingface import HuggingFacePipeline
from langchain.prompts import ChatPromptTemplate

# Path to the model directory
MODEL_PATH = os.path.join(os.getcwd(), "finetunedmodel-merged")

class AgentMessage:
    """Message class for agent communication."""
    
    def __init__(self, content, sender="user", recipient="system"):
        self.id = f"msg_{datetime.now().timestamp()}"
        self.timestamp = datetime.now()
        self.sender = sender
        self.recipient = recipient
        self.content = content
        self.metadata = {}

class CheckInAgent:
    """Simplified Check-in Agent for testing."""
    
    def __init__(self):
        """Initialize the Check-in Agent."""
        self.name = "check_in_agent"
        self.description = "Handles guest check-ins, verifies ID and payment, and updates booking records"
        
        # Load the model
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
        print("✅ Using local quantized model")
        
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
        """Load the local model from the correct snapshot directory."""
        print(f"Loading model from: {MODEL_PATH}")
        
        # Configure 8-bit quantization
        quantization_config = BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_enable_fp32_cpu_offload=True
        )
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_PATH,
            trust_remote_code=True,
            local_files_only=True  # Explicitly use local files only
        )
        
        # Load model with quantization and CUDA support
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            trust_remote_code=True,
            local_files_only=True,  # Explicitly use local files only
            quantization_config=quantization_config,  # Use BitsAndBytesConfig instead of load_in_8bit
            device_map="auto"       # Automatically use CUDA if available
        )
        
        print("✅ Model loaded successfully!")
        return model, tokenizer
    
    async def process(self, booking_id, guest_name, message):
        """Process a check-in request."""
        print(f"Processing check-in for booking ID: {booking_id}")
        
        # Prepare context for the LLM
        context = {
            "booking_id": booking_id,
            "guest_name": guest_name,
            "id_verified": "Yes",
            "payment_verified": "Yes",
            "latest_message": message
        }
        
        # Format the input for the LLM
        formatted_input = f"""
        Booking ID: {context['booking_id']}
        Guest Name: {context['guest_name']}
        ID Verified: {context['id_verified']}
        Payment Verified: {context['payment_verified']}
        
        Latest Message:
        {context['latest_message']}
        """
        
        # Format the prompt first
        formatted_prompt = self.prompt.format(input=formatted_input)
        
        # Then invoke the LLM with the formatted prompt
        llm_response = await self.llm.ainvoke(formatted_prompt)
        
        # Handle the response which might be a string or an object with a content attribute
        if hasattr(llm_response, 'content'):
            response_content = llm_response.content
        else:
            response_content = llm_response
        
        # Simulate checking the booking system
        booking_details = {
            "booking_id": booking_id,
            "guest_name": guest_name,
            "check_in_date": datetime.now().strftime("%Y-%m-%d"),
            "check_out_date": (datetime.now().replace(day=datetime.now().day + 3)).strftime("%Y-%m-%d"),
            "room_type": "Deluxe",
            "number_of_guests": 2,
            "special_requests": "None"
        }
        
        # Determine check-in status
        check_in_status = "completed"
        
        # Assign a room number
        room_number = "301"
        
        # Create the response message
        response_message = AgentMessage(
            content=response_content,
            sender="system",
            recipient="user"
        )
        
        # Return the result
        return {
            "message": response_message,
            "booking_details": booking_details,
            "check_in_status": check_in_status,
            "room_number": room_number,
            "key_issued": True
        }

async def test_check_in_agent():
    """Test the CheckInAgent with a preset query."""
    print("\n--- Testing CheckInAgent ---")
    
    # Initialize the agent
    print("Initializing CheckInAgent...")
    agent = CheckInAgent()
    
    # Test query
    booking_id = "BK12345"
    guest_name = "John Doe"
    message = "I'd like to check in to my room. My booking ID is BK12345."
    
    print(f"\nQuery: {message}")
    
    # Process the query
    result = await agent.process(booking_id, guest_name, message)
    
    # Print the results
    print(f"\nResults:")
    print(f"Check-in status: {result['check_in_status']}")
    print(f"Room number: {result['room_number']}")
    print(f"Key issued: {result['key_issued']}")
    print(f"Booking details: {result['booking_details']}")
    
    # Print the agent's response
    print(f"\nAgent response: {result['message'].content}")
    
    return True

async def main():
    """Run the test script."""
    print("=" * 50)
    print("TESTING CHECK-IN AGENT")
    print("=" * 50)
    
    # Test the check-in agent
    success = await test_check_in_agent()
    
    # Print the overall results
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    print(f"CheckInAgent test: {'SUCCESS' if success else 'FAILED'}")
    print("=" * 50)

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())