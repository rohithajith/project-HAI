"""
Test script for the Hotel AI Assistant agents.

This script tests the agent flow with a preset query to verify that the model is loading
and processing correctly.
"""

import asyncio
import pytest
import os
import sys
from datetime import datetime

# Add the project root to the path so we can import the backend package
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Use absolute imports with package structure
from backend.ai_agents.supervisor import SupervisorAgent
from backend.ai_agents.schemas import AgentMessage, ConversationState

async def test_supervisor_agent():
    """Test the SupervisorAgent with a preset query."""
    print("Initializing SupervisorAgent...")
    agent = SupervisorAgent()
    
    # Create a test conversation state
    state = ConversationState(
        messages=[
            {
                "role": "user",
                "content": "I'd like to check in to my room. My booking ID is BK12345."
            }
        ],
        current_agent=None,
        agent_outputs={}
    )
    
    print("\nProcessing query through SupervisorAgent...")
    try:
        # Process the query through the supervisor agent
        updated_state = await agent.process_supervisor(state)
        
        # Get the agent that the supervisor routed to
        routed_agent = updated_state["current_agent"]
        
        print(f"\nResults:")
        print(f"Routed to agent: {routed_agent}")
        
        # If there are any new messages from the supervisor, print them
        if len(updated_state["messages"]) > 1:
            print(f"Supervisor response: {updated_state['messages'][-1]['content']}")
        
        return True
    except Exception as e:
        print(f"Error processing query: {e}")
        import traceback
        traceback.print_exc()
        return False

@pytest.mark.asyncio
async def test_direct_agent_flow():
    """Test a direct agent flow with a preset query."""
    from backend.ai_agents.agents.check_in_agent import CheckInAgent
    from backend.ai_agents.schemas import CheckInInput
    
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

async def main():
    """Run the test script."""
    print("=" * 50)
    print("TESTING HOTEL AI ASSISTANT AGENTS")
    print("=" * 50)
    
    # Test the supervisor agent
    print("\n[TEST 1] Testing SupervisorAgent...")
    supervisor_success = await test_supervisor_agent()
    
    # Test a direct agent flow
    print("\n[TEST 2] Testing direct agent flow...")
    direct_flow_success = await test_direct_agent_flow()
    
    # Print the overall results
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    print(f"SupervisorAgent test: {'SUCCESS' if supervisor_success else 'FAILED'}")
    print(f"Direct agent flow test: {'SUCCESS' if direct_flow_success else 'FAILED'}")
    print("=" * 50)

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())