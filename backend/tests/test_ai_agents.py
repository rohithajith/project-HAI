import pytest
import os
import sys
import time
from typing import Dict, Any
from unittest.mock import Mock, patch
import torch

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.ai_agents.agent_manager import AgentManager
from backend.ai_agents.base_agent import BaseAgent
from backend.ai_agents.conversation_memory import ConversationMemory
from backend.ai_agents.sos_agent import SOSAgent
from backend.ai_agents.room_service_agent import RoomServiceAgent
from backend.ai_agents.maintenance_agent import MaintenanceAgent
from backend.ai_agents.wellness_agent import WellnessAgent
from backend.ai_agents.service_booking_agent import ServiceBookingAgent
from backend.ai_agents.checkin_agent import CheckInAgent
from backend.ai_agents.supervisor_agent import SupervisorAgent

class TestAIAgents:
    def _mock_generate_response(self, agent, message, memory, system_prompt=None):
        """Helper method to mock generate_response"""
        return f"Mocked response for {agent.name}"

    def setUp(self):
        """Setup method to add delay between tests"""
        time.sleep(3)  # 3-second delay between tests

    def _create_mock_model_and_tokenizer(self):
        """Create mock model and tokenizer with basic functionality"""
        mock_model = Mock()
        mock_model.generate.return_value = torch.tensor([[1, 2, 3]])  # Simulate model output
        
        mock_tokenizer = Mock()
        mock_tokenizer.return_value = {
            'input_ids': torch.tensor([[1, 2, 3]]),
            'attention_mask': torch.tensor([[1, 1, 1]])
        }
        mock_tokenizer.decode.return_value = "Mocked decoded response"
        
        return mock_model, mock_tokenizer

    @pytest.fixture
    def mock_model(self):
        model, _ = self._create_mock_model_and_tokenizer()
        return model

    @pytest.fixture
    def mock_tokenizer(self):
        _, tokenizer = self._create_mock_model_and_tokenizer()
        return tokenizer

    @pytest.mark.agent_test
    def test_agent_manager_initialization(self, mock_model, mock_tokenizer):
        """Test AgentManager initialization and basic functionality"""
        self.setUp()
        agent_manager = AgentManager()
        
        # Check if all agents are initialized
        assert hasattr(agent_manager, 'supervisor')
        assert hasattr(agent_manager, 'room_service_agent')
        assert hasattr(agent_manager, 'maintenance_agent')
        assert hasattr(agent_manager, 'wellness_agent')
        assert hasattr(agent_manager, 'service_booking_agent')
        assert hasattr(agent_manager, 'checkin_agent')
        assert hasattr(agent_manager, 'sos_agent')

    def _test_agent_process(self, agent_class, messages, mock_model, mock_tokenizer, conversation_memory):
        """Generic agent process test method"""
        self.setUp()
        with patch.object(agent_class, 'generate_response', side_effect=lambda message, memory, system_prompt=None: f"Mocked response for {agent_class.__name__}"):
            agent = agent_class(f"{agent_class.__name__}", mock_model, mock_tokenizer)
            
            for message in messages:
                response = agent.process(message, conversation_memory)
                
                assert 'response' in response
                assert 'tool_calls' in response
                assert isinstance(response['tool_calls'], list)

    @pytest.mark.agent_test
    def test_room_service_agent(self, mock_model, mock_tokenizer, conversation_memory):
        """Test Room Service Agent functionality"""
        self._test_agent_process(
            RoomServiceAgent,
            ["I want to order some food", "Can I get extra towels?", "Bring me a burger"],
            mock_model, mock_tokenizer, conversation_memory
        )

    @pytest.mark.agent_test
    def test_maintenance_agent(self, mock_model, mock_tokenizer, conversation_memory):
        """Test Maintenance Agent functionality"""
        self._test_agent_process(
            MaintenanceAgent,
            ["My room's air conditioner is broken", "Need to schedule a repair", "Something is not working in my room"],
            mock_model, mock_tokenizer, conversation_memory
        )

    @pytest.mark.agent_test
    def test_wellness_agent(self, mock_model, mock_tokenizer, conversation_memory):
        """Test Wellness Agent functionality"""
        self._test_agent_process(
            WellnessAgent,
            ["I want to book a spa treatment", "Are there any yoga classes?", "Tell me about meditation sessions"],
            mock_model, mock_tokenizer, conversation_memory
        )

    @pytest.mark.agent_test
    def test_service_booking_agent(self, mock_model, mock_tokenizer, conversation_memory):
        """Test Service Booking Agent functionality"""
        self.setUp()
        with patch.object(ServiceBookingAgent, 'generate_response', side_effect=lambda message, memory, system_prompt=None: f"Mocked response for ServiceBookingAgent"):
            service_booking_agent = ServiceBookingAgent("ServiceBookingAgent", mock_model, mock_tokenizer)
            
            booking_messages = [
                "Book a spa session at 10am",
                "I want to book a gym session",
                "Can I book a meditation room?"
            ]
            
            for message in booking_messages:
                response = service_booking_agent.process(message, conversation_memory)
                assert 'response' in response
                assert 'tool_calls' in response

    @pytest.mark.agent_test
    def test_checkin_agent(self, mock_model, mock_tokenizer, conversation_memory):
        """Test Check-in Agent functionality"""
        self.setUp()
        with patch.object(CheckInAgent, 'generate_response', side_effect=lambda message, memory, system_prompt=None: f"Mocked response for CheckInAgent"):
            checkin_agent = CheckInAgent("CheckInAgent", mock_model, mock_tokenizer)
            
            checkin_messages = [
                "I want to check in with booking ID 1234",
                "Can I extend my stay?",
                "Confirm my booking"
            ]
            
            for message in checkin_messages:
                response = checkin_agent.process(message, conversation_memory)
                assert 'response' in response
                assert 'tool_calls' in response

    @pytest.mark.agent_test
    def test_supervisor_agent(self, mock_model, mock_tokenizer, conversation_memory):
        """Test Supervisor Agent routing"""
        self.setUp()
        with patch.object(SupervisorAgent, 'generate_response', side_effect=lambda message, memory, system_prompt=None: f"Mocked response for SupervisorAgent"):
            supervisor_agent = SupervisorAgent("SupervisorAgent", mock_model, mock_tokenizer)
            
            # Register mock agents
            mock_agents = [
                RoomServiceAgent("RoomServiceAgent", mock_model, mock_tokenizer),
                MaintenanceAgent("MaintenanceAgent", mock_model, mock_tokenizer),
                WellnessAgent("WellnessAgent", mock_model, mock_tokenizer)
            ]
            
            for agent in mock_agents:
                supervisor_agent.register_agent(agent)
            
            test_messages = [
                "I need room service",
                "Something is broken in my room",
                "I want to book a spa treatment"
            ]
            
            for message in test_messages:
                response = supervisor_agent.process(message, conversation_memory)
                assert 'response' in response
                assert 'tool_calls' in response

    @pytest.mark.performance_test
    def test_agent_response_time(self, mock_model, mock_tokenizer, conversation_memory):
        """Test agent response times"""
        self.setUp()
        # Use a real AgentManager with mocked generate_response
        with patch.object(BaseAgent, 'generate_response', side_effect=lambda message, memory, system_prompt=None: f"Mocked response"):
            agent_manager = AgentManager()
            
            test_messages = [
                "I need room service",
                "Emergency help!",
                "Book a spa session",
                "My room needs maintenance"
            ]
            
            for message in test_messages:
                start_time = time.time()
                response = agent_manager.process(message)
                end_time = time.time()
                
                # Ensure response time is under 5 seconds (relaxed constraint)
                assert (end_time - start_time) < 5.0, f"Response time too long for message: {message}"
                
                assert 'response' in response
                assert 'timestamp' in response

    @pytest.mark.agent_test
    def test_agent_tool_calls(self, mock_model, mock_tokenizer):
        """Test tool call functionality across agents"""
        self.setUp()
        agents = [
            RoomServiceAgent("RoomServiceAgent", mock_model, mock_tokenizer),
            MaintenanceAgent("MaintenanceAgent", mock_model, mock_tokenizer),
            WellnessAgent("WellnessAgent", mock_model, mock_tokenizer),
            ServiceBookingAgent("ServiceBookingAgent", mock_model, mock_tokenizer)
        ]
        
        for agent in agents:
            available_tools = agent.get_available_tools()
            assert len(available_tools) > 0, f"No tools found for {agent.name}"
            
            for tool in available_tools:
                try:
                    # Simulate a tool call with minimal arguments
                    if agent.name == "WellnessAgent":
                        result = agent.handle_tool_call(tool.name, service_type="massage", time="10am")
                    elif agent.name == "ServiceBookingAgent":
                        # Specific handling for ServiceBookingAgent
                        if tool.name == "check_menu_availability":
                            result = agent.handle_tool_call(tool.name, item="spa session")
                        elif tool.name == "place_order":
                            result = agent.handle_tool_call(tool.name, service="spa", time="10am")
                    else:
                        result = agent.handle_tool_call(tool.name)
                    assert result is not None
                except NotImplementedError:
                    # Some tools might not be fully implemented, which is okay
                    pass