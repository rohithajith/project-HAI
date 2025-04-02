from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import asyncio
from local_model_chatbot import load_model_and_tokenizer

from .supervisor_agent import SupervisorAgent
from .checkin_agent import CheckInAgent
from .room_service_agent import RoomServiceAgent
from .wellness_agent import WellnessAgent
from .services_booking_agent import ServicesBookingAgent
from .promotion_agent import PromotionAgent
from .base_agent import AgentOutput
from .error_handler import (
    error_handler, 
    with_error_handling, 
    AgentError, 
    ProcessingError,
    ValidationError,
    ErrorMetadata
)

class AgentManagerCorrected:
    """Manages the multi-agent system using local model."""
    
    def __init__(self):
        # Load local model
        self.model, self.tokenizer, self.device = load_model_and_tokenizer()
        if not all([self.model, self.tokenizer, self.device]):
            raise Exception("Failed to load local model and tokenizer")
            
        # Initialize supervisor with local model
        self.supervisor = SupervisorAgent()
        self.supervisor.model = self.model
        self.supervisor.tokenizer = self.tokenizer
        self.supervisor.device = self.device
        
        # Initialize conversation storage
        self.conversation_storage_path = Path("data/conversations")
        self.conversation_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize and register specialized agents
        self._register_agents()
        
        # Build the workflow
        self.supervisor.build_workflow()
    
    def _register_agents(self):
        """Register all specialized agents with the supervisor."""
        try:
            # Register room service agent (primary for towel requests)
            room_service_agent = RoomServiceAgent()
            room_service_agent.model = self.model
            room_service_agent.tokenizer = self.tokenizer
            room_service_agent.device = self.device
            self.supervisor.register_agent(room_service_agent)
            
            # Register other agents
            agents = [
                CheckInAgent(),
                WellnessAgent(),
                ServicesBookingAgent(),
                PromotionAgent()
            ]
            
            for agent in agents:
                agent.model = self.model
                agent.tokenizer = self.tokenizer
                agent.device = self.device
                self.supervisor.register_agent(agent)
                
        except Exception as e:
            raise ProcessingError(
                f"Failed to register agents: {str(e)}",
                metadata=ErrorMetadata(
                    severity="critical",
                    category="initialization",
                    context={"component": "agent_registration"}
                )
            )
    
    def process(self, message: str, history: Optional[List[Dict[str, Any]]] = None) -> AgentOutput:
        """
        Process a message through the multi-agent system.
        
        Args:
            message: The user's message
            history: Optional conversation history
            
        Returns:
            AgentOutput containing the response and any notifications
        """
        if not message.strip():
            return AgentOutput(
                response="Message cannot be empty",
                notifications=[{
                    "type": "error",
                    "severity": "warning",
                    "message": "Empty message received"
                }]
            )
            
        if history is None:
            history = []
            
        try:
            # Process message through supervisor's workflow
            response = self.supervisor.process_message(message, history)
            return response
            
        except Exception as e:
            return AgentOutput(
                response="I apologize, but I encountered an error processing your request. Please try again.",
                notifications=[{
                    "type": "error",
                    "severity": "error",
                    "message": str(e)
                }]
            )

# Create singleton instance
agent_manager_corrected = AgentManagerCorrected()