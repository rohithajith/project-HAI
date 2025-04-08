"""
Agent Registration: The _register_agents method correctly instantiates specialized agents and registers them with the SupervisorAgent instance using self.supervisor.register_agent(agent). This ensures the supervisor knows which agents are available.
Processing Logic (process method):
Direct Call (Fast Path): For messages containing specific keywords related to room service (e.g., "towel", "food", "order"), the manager directly finds the room_service_agent from the supervisor's list and calls await room_service_agent.process(...). This bypasses the supervisor for these common requests.
Indirect Call (Delegation): For messages not matching the fast path keywords, the manager correctly delegates the task to the supervisor by calling await self.supervisor.process(...). The supervisor then handles selecting and calling the appropriate specialized agent.
Asynchronous Calls: Both the direct calls to the room service agent and the delegation call to the supervisor correctly use await, matching the async def process signatures of the respective methods.
"""
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
            # Register room service agent (primary for towel requests) with high priority
            room_service_agent = RoomServiceAgent()
            room_service_agent.model = self.model
            room_service_agent.tokenizer = self.tokenizer
            room_service_agent.device = self.device
            # Ensure this agent has highest priority for handling food and towel requests
            room_service_agent.priority = 10  # Increase priority to ensure it handles relevant requests
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
    
    async def process(self, message: str, history: Optional[List[Dict[str, Any]]] = None) -> AgentOutput: # Added async
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
            # Check for direct room service related keywords for faster processing
            message_lower = message.lower()
            if any(keyword in message_lower for keyword in
                  ["towel", "room service", "food", "order", "burger", "fries"]):
                # Process directly with room service agent
                room_service_agent = next(
                    (agent for agent in self.supervisor.agents.values()
                     if agent.name == "room_service_agent"),
                    None
                )
                
                if room_service_agent:
                    # Room service agent's process is async, so await it
                    response = await room_service_agent.process(message, history)
                    
                    # No need for manual event loop handling here as we are in an async method
                    
                    # Add agent info to response if not present
                    if isinstance(response, AgentOutput) and not any(
                        n.get('agent') == 'room_service_agent' for n in response.notifications
                    ):
                        response.notifications.append({
                            'agent': 'room_service_agent',
                            'type': 'agent_info'
                        })
                        
                    return response
            
            # Process through standard workflow for other messages via the supervisor
            response = await self.supervisor.process(message, history) # Corrected method name

            # Note: Supervisor's process method is already async, no need for separate event loop handling here.

            return response
            
        except AgentError as e:
            # Handle known agent errors using the error handler
            error_response = error_handler.create_error_response(e)
            # Convert ErrorResponse to AgentOutput for consistency
            return AgentOutput(
                response=error_response.message,
                notifications=[{
                    "type": "error",
                    "severity": e.metadata.severity,
                    "message": error_response.details or str(e),
                    "error_code": e.error_code,
                    "agent": e.metadata.agent_name or "agent_manager"
                }]
            )
        except Exception as e:
            # Handle unexpected errors
            unexpected_error = ProcessingError(
                message=f"Unexpected error in AgentManager: {str(e)}",
                metadata=ErrorMetadata(
                    severity="critical",
                    category="unexpected",
                    context={"component": "AgentManagerCorrected.process"}
                )
            )
            error_handler.log_error(unexpected_error)
            error_response = error_handler.create_error_response(unexpected_error)
            return AgentOutput(
                response=error_response.message,
                notifications=[{
                    "type": "error",
                    "severity": "critical",
                    "message": "An unexpected system error occurred.",
                    "error_code": unexpected_error.error_code,
                    "agent": "agent_manager"
                }]
            )

# Create singleton instance
agent_manager_corrected = AgentManagerCorrected()