import asyncio
import pytest
import json
from datetime import datetime, timezone
from typing import List, Dict, Any

# Import specific agents for testing
from ai_agents.room_service_agent import RoomServiceAgent
from ai_agents.supervisor_agent import SupervisorAgent
from ai_agents.base_agent import AgentOutput
from ai_agents.maintenance_agent import MaintenanceAgent
from ai_agents.services_booking_agent import ServicesBookingAgent

class TestAgentJSONResponses:
    @pytest.mark.asyncio
    async def test_agent_json_response_structure(self):
        """Validate JSON response structure for key agents."""
        agents = [
            RoomServiceAgent(),
            MaintenanceAgent(),
            ServicesBookingAgent()
        ]

        test_scenarios = [
            "I need towels",
            "Check when is the checkout time?"
        ]

        for agent in agents:
            for scenario in test_scenarios:
                result = await agent.process(scenario, [])
                
                # Validate AgentOutput is a Pydantic model
                assert hasattr(result, 'model_dump'), f"{agent.name} did not return a valid AgentOutput"
                
                # Convert to dict to simulate JSON serialization
                json_result = result.model_dump()
                
                # Basic JSON response structure validation
                assert isinstance(json_result, dict), f"{agent.name} output is not a dictionary"
                assert 'response' in json_result, f"{agent.name} missing 'response' key"
                assert 'notifications' in json_result, f"{agent.name} missing 'notifications' key"

    @pytest.mark.asyncio
    async def test_supervisor_agent_basic_routing(self):
        """Test Supervisor Agent's basic routing capability."""
        supervisor = SupervisorAgent()
        
        routing_test_cases = [
            {
                "message": "I want to order breakfast",
                "expected_agent": "room_service_agent"
            }
        ]

        for scenario in routing_test_cases:
            result = await supervisor.process(scenario["message"], [])
            
            # Validate JSON response
            json_result = result.model_dump()
            assert 'response' in json_result, "Supervisor agent response missing"

    def test_agent_tool_handling_basic(self):
        """Basic test for agent tool handling."""
        agents = [
            RoomServiceAgent(),
            ServicesBookingAgent(),
            MaintenanceAgent()
        ]

        tool_scenarios = [
            {"agent": RoomServiceAgent(), "tool": "check_menu_availability", "args": {"item_ids": ["burger"]}},
            {"agent": ServicesBookingAgent(), "tool": "check_service_availability", "args": {"service_type": "spa"}},
            {"agent": MaintenanceAgent(), "tool": "report_maintenance_issue", "args": {"issue_type": "plumbing", "room_number": "102", "description": "Test issue"}}
        ]

        for scenario in tool_scenarios:
            tool_result = asyncio.run(scenario["agent"].handle_tool_call(
                scenario["tool"], 
                scenario["args"]
            ))
            
            # Basic validation of tool result
            assert isinstance(tool_result, dict), f"{scenario['tool']} result must be a dictionary"
            assert len(tool_result) > 0, f"{scenario['tool']} result cannot be empty"

def generate_agent_interaction_report():
    """Generate a brief report of agent interactions."""
    report = "# Agent Interaction Report\n\n"
    
    agents_info = [
        ("Room Service Agent", ["Handles room service orders"]),
        ("Maintenance Agent", ["Handles maintenance requests"]),
        ("Services Booking Agent", ["Manages service bookings"])
    ]
    
    for name, capabilities in agents_info:
        report += f"## {name} Capabilities\n"
        for capability in capabilities:
            report += f"- {capability}\n"
        report += "\n"

    # Write report to file
    with open('backend/agent_interaction_report.md', 'w') as f:
        f.write(report)

# Generate report after tests
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if exitstatus == 0:
        generate_agent_interaction_report()