"""
Test script for a single agent in the Hotel AI Assistant.

This script tests a single agent directly, without the full agent flow or the supervisor.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import the agent modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Use relative imports
from agents.check_in_agent import CheckInAgent
from agents.room_service_agent import RoomServiceAgent
from agents.wellness_agent import WellnessAgent
from schemas import AgentMessage, CheckInInput, RoomServiceInput, WellnessInput

async def test_check_in_agent():
    """Test the CheckInAgent with a preset query."""
    print("\n--- Testing CheckInAgent ---")
    
    # Initialize the agent
    print("Initializing CheckInAgent...")
    agent = CheckInAgent()
    
    # Create a test message
    messages = [
        AgentMessage(
            id="msg_1",
            timestamp=datetime.now(),
            sender="user",
            recipient="system",
            content="I'd like to check in to my room. My booking ID is BK12345.",
            metadata={}
        )
    ]
    
    # Create the input for the agent
    agent_input = CheckInInput(
        messages=messages,
        booking_id="BK12345",
        guest_name="John Doe",
        id_verification=True,
        payment_verification=True
    )
    
    print("\nProcessing query through CheckInAgent...")
    try:
        # Process the input with the agent
        agent_output = await agent.process(agent_input)
        
        print(f"\nResults:")
        print(f"Check-in status: {agent_output.check_in_status}")
        print(f"Room number: {agent_output.room_number}")
        print(f"Key issued: {agent_output.key_issued}")
        
        # Print the agent's response
        if agent_output.messages:
            print(f"\nAgent response: {agent_output.messages[0].content}")
        
        return True
    except Exception as e:
        print(f"Error processing query: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_room_service_agent():
    """Test the RoomServiceAgent with a preset query."""
    print("\n--- Testing RoomServiceAgent ---")
    
    # Initialize the agent
    print("Initializing RoomServiceAgent...")
    agent = RoomServiceAgent()
    
    # Create a test message
    messages = [
        AgentMessage(
            id="msg_1",
            timestamp=datetime.now(),
            sender="user",
            recipient="system",
            content="Can I get some extra towels and pillows delivered to room 301?",
            metadata={}
        )
    ]
    
    # Create the input for the agent
    agent_input = RoomServiceInput(
        messages=messages,
        room_number="301",
        request_type="towels and pillows",
        quantity=2,
        special_instructions="Please deliver within the next hour."
    )
    
    print("\nProcessing query through RoomServiceAgent...")
    try:
        # Process the input with the agent
        agent_output = await agent.process(agent_input)
        
        print(f"\nResults:")
        print(f"Request ID: {agent_output.request_id}")
        print(f"Status: {agent_output.status}")
        print(f"Estimated delivery time: {agent_output.estimated_delivery_time}")
        print(f"Assigned staff: {agent_output.assigned_staff}")
        
        # Print the agent's response
        if agent_output.messages:
            print(f"\nAgent response: {agent_output.messages[0].content}")
        
        return True
    except Exception as e:
        print(f"Error processing query: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_wellness_agent():
    """Test the WellnessAgent with a preset query."""
    print("\n--- Testing WellnessAgent ---")
    
    # Initialize the agent
    print("Initializing WellnessAgent...")
    agent = WellnessAgent()
    
    # Create a test message
    messages = [
        AgentMessage(
            id="msg_1",
            timestamp=datetime.now(),
            sender="user",
            recipient="system",
            content="I'd like to do a guided meditation session.",
            metadata={}
        )
    ]
    
    # Create the input for the agent
    agent_input = WellnessInput(
        messages=messages,
        session_type="meditation",
        duration=5,
        preferences={"focus": "relaxation", "experience_level": "beginner"}
    )
    
    print("\nProcessing query through WellnessAgent...")
    try:
        # Process the input with the agent
        agent_output = await agent.process(agent_input)
        
        print(f"\nResults:")
        print(f"Session ID: {agent_output.session_id}")
        print(f"Status: {agent_output.status}")
        
        # Print the agent's response
        if agent_output.messages:
            print(f"\nAgent response: {agent_output.messages[0].content}")
        
        return True
    except Exception as e:
        print(f"Error processing query: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the test script."""
    print("=" * 50)
    print("TESTING SINGLE AGENT")
    print("=" * 50)
    
    # Select which agent to test
    agent_type = input("Select agent to test (1=CheckIn, 2=RoomService, 3=Wellness): ")
    
    if agent_type == "1":
        success = await test_check_in_agent()
    elif agent_type == "2":
        success = await test_room_service_agent()
    elif agent_type == "3":
        success = await test_wellness_agent()
    else:
        print(f"Invalid agent type: {agent_type}")
        success = False
    
    # Print the overall results
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    print(f"Agent test: {'SUCCESS' if success else 'FAILED'}")
    print("=" * 50)

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())