"""
Selection Logic (_select_next_agent): The method uses a two-tiered approach:
It first attempts to match keywords in the user's message against predefined lists associated with specific agents (agent_keyword_map). If a match is found, that agent is selected immediately.
If no keywords match, it iterates through all registered agents, calling their should_handle method. Agents returning True are considered eligible.
From the eligible agents (if any), the one with the highest priority value is chosen.
If no agent is eligible, None is returned.
Calling Logic (process):
It correctly calls _select_next_agent to determine the handler.
It handles the case where no agent is selected by returning an appropriate message.
If an agent is selected, it correctly calls await selected_agent.process(message, history) to execute the chosen agent's logic.
It includes error handling for both expected AgentError types and unexpected Exception occurrences during selection or processing.
"""
from typing import List, Dict, Any, Optional, Tuple
import torch
import asyncio
from datetime import datetime, timezone
from pydantic import BaseModel, Field # Removed LangGraph imports
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from .base_agent import BaseAgent, AgentOutput
from .error_handler import error_handler, AgentError, ProcessingError, ErrorMetadata # Import error handling components
# LlamaWrapper removed as it's not directly used here; model/tokenizer are passed from AgentManager
# Removed unused SupervisorState class
class SupervisorAgent:
    """Coordinates workflow between specialized agents."""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        # self.workflow: Optional[Graph] = None # Workflow not used in current logic
        self.model = None
        self.tokenizer = None
        self.device = None
        
        # Pre-register common agents during initialization
        from .room_service_agent import RoomServiceAgent
        from .maintenance_agent import MaintenanceAgent
        from .services_booking_agent import ServicesBookingAgent
        from .wellness_agent import WellnessAgent
        from .promotion_agent import PromotionAgent
        
        for agent_class in [
            RoomServiceAgent, 
            MaintenanceAgent, 
            ServicesBookingAgent, 
            WellnessAgent, 
            PromotionAgent
        ]:
            self.register_agent(agent_class())
        
    def register_agent(self, agent: BaseAgent):
        """Register a specialized agent with the supervisor."""
        self.agents[agent.name] = agent
        
    # Removed build_workflow method as LangGraph is not used in the current process logic
    def _select_next_agent(self, message: str, history: List[Dict[str, Any]]) -> Optional[BaseAgent]:
        """Select the most appropriate agent to handle the current message."""
        message_lower = message.lower()
        
        # Predefined keyword mappings for direct agent routing
        agent_keyword_map = {
            "room_service_agent": ["towel", "room service", "food", "order", "burger", "fries", "breakfast", "lunch", "dinner", "meal"],
            "maintenance_agent": ["repair", "fix", "broken", "maintenance", "issue", "problem"],
            "services_booking_agent": ["book", "reservation", "schedule", "appointment"],
            "wellness_agent": ["spa", "treatment", "massage", "wellness", "relax"],
            "promotion_agent": ["discount", "offer", "promotion", "deal", "special"]
        }
        
        # First, try direct keyword matching
        for agent_name, keywords in agent_keyword_map.items():
            if any(keyword in message_lower for keyword in keywords):
                return self.agents.get(agent_name)
        
        # Fallback to normal agent selection
        eligible_agents = [
            agent for agent in self.agents.values()
            if agent.should_handle(message, history)
        ]
        
        if not eligible_agents:
            return None
            
        # Return the highest priority eligible agent
        return max(eligible_agents, key=lambda x: x.priority)
    
    async def process(self, message: str, history: List[Dict[str, Any]]) -> AgentOutput:
        """Async process method to handle message routing and agent selection."""
        try:
            # Select the most appropriate agent
            selected_agent = self._select_next_agent(message, history)
            
            if not selected_agent:
                return AgentOutput(
                    response="I'm unable to assist with your request at the moment. Could you please rephrase or provide more details?",
                    notifications=[{
                        "type": "routing_failure",
                        "message": "No suitable agent found for the request"
                    }]
                )
            
            # Process with the selected agent
            response = await selected_agent.process(message, history)
            
            # Enhance notifications with routing information
            response.notifications.append({
                "type": "agent_routing",
                "selected_agent": selected_agent.name,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # Modify response to include agent name for routing test
            response.response = f"[{selected_agent.name}] {response.response}"
            
            return response
        
        except AgentError as e:
            # Handle known agent errors from the selected agent's process method
            # Enrich metadata if possible
            e.metadata.agent_name = e.metadata.agent_name or selected_agent.name if selected_agent else "supervisor"
            error_handler.log_error(e)
            error_response = error_handler.create_error_response(e)
            return AgentOutput(
                response=error_response.message,
                notifications=[{
                    "type": "error",
                    "severity": e.metadata.severity,
                    "message": error_response.details or str(e),
                    "error_code": e.error_code,
                    "agent": e.metadata.agent_name
                }]
            )
        except Exception as e:
            # Handle unexpected errors during supervisor processing
            unexpected_error = ProcessingError(
                message=f"Unexpected error in SupervisorAgent: {str(e)}",
                metadata=ErrorMetadata(
                    severity="critical",
                    category="supervisor_unexpected",
                    agent_name="supervisor",
                    context={"component": "SupervisorAgent.process"}
                )
            )
            error_handler.log_error(unexpected_error)
            error_response = error_handler.create_error_response(unexpected_error)
            return AgentOutput(
                response=error_response.message,
                notifications=[{
                    "type": "error",
                    "severity": "critical",
                    "message": "An unexpected system error occurred during request routing.",
                    "error_code": unexpected_error.error_code,
                    "agent": "supervisor"
                }]
            )