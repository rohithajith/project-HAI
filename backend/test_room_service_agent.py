import asyncio
import os
import json
from ai_agents.room_service_agent import RoomServiceAgent
from ai_agents.agent_logger import AgentLogger

async def test_room_service_agent_scenarios():
    """
    Demonstrate RoomServiceAgent functionality with logging and JSON output.
    Scenarios cover different types of requests to show frontend update mechanisms.
    """
    agent = RoomServiceAgent()
    
    # Test scenarios
    scenarios = [
        {
            "message": "I need towels in room 202",
            "description": "Towel request scenario"
        },
        {
            "message": "Can I see the room service menu?",
            "description": "Menu inquiry scenario"
        },
        {
            "message": "I want to order a burger and fries for room 202",
            "description": "Food order scenario"
        }
    ]
    
    # Run through scenarios
    for scenario in scenarios:
        print(f"\n--- {scenario['description']} ---")
        print(f"Message: {scenario['message']}")
        
        # Process the message
        response = await agent.process(scenario['message'], [])
        
        # Print response details
        print("Response:", response.response)
        print("\nNotifications:")
        for notification in response.notifications:
            print(json.dumps(notification, indent=2))
        
        # Retrieve the most recent log file
        recent_logs = AgentLogger.get_recent_logs(agent.name, limit=1)
        
        if recent_logs:
            with open(recent_logs[0], 'r') as log_file:
                log_data = json.load(log_file)
                print("\nFrontend Update Instructions:")
                print(json.dumps(log_data.get('frontend_update', {}), indent=2))
        
        print("-" * 50)

# Run the test
if __name__ == "__main__":
    asyncio.run(test_room_service_agent_scenarios())