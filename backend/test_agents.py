import asyncio
import pytest
from datetime import datetime, timezone
from typing import List, Dict, Any

# Import specific agents for testing
from ai_agents.room_service_agent import RoomServiceAgent
from ai_agents.supervisor_agent import SupervisorAgent
from ai_agents.base_agent import AgentOutput

class TestRoomServiceAndAdminAgents:
    def test_room_service_agent_initialization(self):
        """Test Room Service Agent initialization."""
        agent = RoomServiceAgent()
        
        # Check basic agent properties
        assert hasattr(agent, 'name')
        assert agent.name == "room_service_agent"
        assert agent.priority == 10
        assert len(agent.tools) > 0
        
        # Verify specific tools
        tool_names = [tool.name for tool in agent.tools]
        assert "check_menu_availability" in tool_names
        assert "place_order" in tool_names

    @pytest.mark.asyncio
    async def test_room_service_order_scenarios(self):
        """Comprehensive test scenarios for Room Service Agent."""
        agent = RoomServiceAgent()
        scenarios = [
            {
                "message": "I am in room 102. I would like to order a burger and fries",
                "expected_keywords": ["burger", "fries", "room 102"],
                "notification_type": "order_started"
            },
            {
                "message": "Can I see the menu?",
                "expected_keywords": ["menu", "breakfast", "dining"],
                "notification_type": "menu_viewed"
            },
            {
                "message": "I need some towels",
                "expected_keywords": ["towels", "fresh"],
                "notification_type": "housekeeping_request"
            }
        ]

        for scenario in scenarios:
            # Simulate processing delay
            await asyncio.sleep(2)

            # Process message
            result = await agent.process(scenario["message"], [])

            # Validate result
            assert result is not None
            assert isinstance(result, AgentOutput)

            # Check response contains expected keywords
            response_lower = result.response.lower()
            for keyword in scenario["expected_keywords"]:
                assert keyword.lower() in response_lower, f"Keyword '{keyword}' not found in response"

            # Validate notifications
            assert len(result.notifications) > 0
            notification = result.notifications[0]
            assert notification.get('type') == scenario["notification_type"]
            assert notification.get('agent') == 'room_service_agent'

    def test_room_service_agent_tool_handling(self):
        """Test Room Service Agent tool handling."""
        agent = RoomServiceAgent()

        # Test menu availability check
        menu_check_result = asyncio.run(agent.handle_tool_call(
            "check_menu_availability", 
            {"item_ids": ["burger", "fries"]}
        ))
        assert "available_items" in menu_check_result
        assert "estimated_wait" in menu_check_result

        # Test order placement
        order_result = asyncio.run(agent.handle_tool_call(
            "place_order", 
            {
                "room_number": "102", 
                "order_items": ["burger", "fries"],
                "special_instructions": "Extra crispy fries"
            }
        ))
        assert "order_id" in order_result
        assert order_result["status"] == "confirmed"
        assert order_result["room_number"] == "102"

    def test_supervisor_agent_initialization(self):
        """Test Supervisor Agent initialization."""
        agent = SupervisorAgent()
        
        # Check basic agent properties
        assert hasattr(agent, 'agents'), "Supervisor Agent should have 'agents' attribute"
        assert isinstance(agent.agents, dict), "'agents' should be a dictionary"
        
        # Check workflow-related attributes
        assert hasattr(agent, 'workflow'), "Supervisor Agent should have 'workflow' attribute"
        assert hasattr(agent, 'model'), "Supervisor Agent should have 'model' attribute"
        assert hasattr(agent, 'tokenizer'), "Supervisor Agent should have 'tokenizer' attribute"
        assert hasattr(agent, 'device'), "Supervisor Agent should have 'device' attribute"

    def test_supervisor_agent_methods(self):
        """Test Supervisor Agent methods."""
        agent = SupervisorAgent()
        
        # Test register_agent method
        mock_base_agent = type('MockBaseAgent', (), {
            'name': 'mock_agent',
            'priority': 5,
            'should_handle': lambda self, message, history: True,
            'process': lambda self, message, history: AgentOutput(response="Mock response")
        })()
        
        agent.register_agent(mock_base_agent)
        
        # Verify agent was registered
        assert 'mock_agent' in agent.agents
        assert agent.agents['mock_agent'] == mock_base_agent

def generate_agent_interaction_report():
    """Generate a report of agent interactions and capabilities."""
    report = "# Agent Interaction Report\n\n"
    
    # Room Service Agent Report
    report += "## Room Service Agent Capabilities\n"
    report += "- Handles room service orders\n"
    report += "- Manages menu inquiries\n"
    report += "- Processes housekeeping requests\n\n"

    # Supervisor Agent Report
    report += "## Supervisor Agent Capabilities\n"
    report += "- Coordinates workflow between agents\n"
    report += "- Selects appropriate agent for requests\n"
    report += "- Manages agent interactions\n"

    # Write report to file
    with open('backend/agent_interaction_report.md', 'w') as f:
        f.write(report)

    print("Agent interaction report generated at backend/agent_interaction_report.md")

# Generate report after tests
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if exitstatus == 0:
        generate_agent_interaction_report()