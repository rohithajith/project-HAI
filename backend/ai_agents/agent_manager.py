from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import asyncio

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

class AgentManager:
    """Manages the multi-agent system and coordinates agent interactions."""
    
    def __init__(self):
        # Initialize supervisor
        self.supervisor = SupervisorAgent()
        
        # Initialize conversation storage
        self.conversation_storage_path = Path("data/conversations")
        self.conversation_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize and register specialized agents
        self._register_agents()
        
        # Build the workflow
        self.supervisor.build_workflow()
    
    @with_error_handling({"component": "agent_registration"})
    async def _register_agents(self):
        """Register all specialized agents with the supervisor."""
        try:
            # Register check-in agent
            checkin_agent = CheckInAgent()
            self.supervisor.register_agent(checkin_agent)
            
            # Register room service agent
            room_service_agent = RoomServiceAgent()
            self.supervisor.register_agent(room_service_agent)
            
            # Register wellness agent
            wellness_agent = WellnessAgent()
            self.supervisor.register_agent(wellness_agent)
            
            # Register services booking agent
            services_booking_agent = ServicesBookingAgent()
            self.supervisor.register_agent(services_booking_agent)
            
            # Register promotion agent
            promotion_agent = PromotionAgent()
            self.supervisor.register_agent(promotion_agent)
            
        except Exception as e:
            raise ProcessingError(
                f"Failed to register agents: {str(e)}",
                metadata=ErrorMetadata(
                    severity="critical",
                    category="initialization",
                    context={"component": "agent_registration"}
                )
            )
    
    @with_error_handling({"component": "message_processing"})
    async def process_message(self, 
                            message: str, 
                            conversation_id: str,
                            history: Optional[List[Dict[str, Any]]] = None) -> AgentOutput:
        """
        Process an incoming message through the multi-agent system.
        
        Args:
            message: The user's message
            conversation_id: Unique identifier for the conversation
            history: Optional conversation history
            
        Returns:
            AgentOutput containing the response and any notifications
        """
        if not message.strip():
            raise ValidationError(
                "Message cannot be empty",
                metadata=ErrorMetadata(
                    severity="warning",
                    category="validation",
                    context={
                        "conversation_id": conversation_id,
                        "component": "message_processing"
                    }
                )
            )
            
        if history is None:
            history = await self.get_conversation_history(conversation_id)
            
        error_context = {
            "conversation_id": conversation_id,
            "component": "message_processing",
            "history_length": len(history) if history else 0
        }
            
        try:
            # Process message through supervisor's workflow
            response = await error_handler.handle_with_retry(
                self.supervisor.process_message,
                message=message,
                history=history,
                error_context=error_context
            )
            
            # Log conversation for GDPR compliance
            await self._log_conversation(conversation_id, message, response)
            
            return response
            
        except AgentError:
            # Re-raise agent errors to be handled by decorator
            raise
        except Exception as e:
            raise ProcessingError(
                f"Failed to process message: {str(e)}",
                metadata=ErrorMetadata(
                    severity="error",
                    category="processing",
                    context=error_context
                )
            )
    
    @with_error_handling({"component": "conversation_logging"})
    async def _log_conversation(self, 
                              conversation_id: str, 
                              message: str, 
                              response: AgentOutput):
        """
        Log conversation for GDPR compliance and monitoring.
        
        Args:
            conversation_id: Unique identifier for the conversation
            message: The user's message
            response: The system's response
        """
        try:
            log_file = self.conversation_storage_path / f"{conversation_id}.jsonl"
            
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "message": message,
                "response": response.model_dump(),
                "metadata": {
                    "conversation_id": conversation_id
                }
            }
            
            # Append to log file
            async with aiofiles.open(log_file, 'a') as f:
                await f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            raise ProcessingError(
                f"Failed to log conversation: {str(e)}",
                metadata=ErrorMetadata(
                    severity="warning",
                    category="logging",
                    context={
                        "conversation_id": conversation_id,
                        "component": "conversation_logging"
                    }
                )
            )

    @with_error_handling({"component": "conversation_history"})
    async def get_conversation_history(self, 
                                     conversation_id: str,
                                     max_messages: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a given conversation ID.
        Implements GDPR compliance for data access.
        
        Args:
            conversation_id: Unique identifier for the conversation
            max_messages: Maximum number of messages to retrieve
            
        Returns:
            List of conversation messages
        """
        try:
            log_file = self.conversation_storage_path / f"{conversation_id}.jsonl"
            
            if not log_file.exists():
                return []
                
            history = []
            async with aiofiles.open(log_file, 'r') as f:
                async for line in f:
                    entry = json.loads(line)
                    history.append({
                        "role": "user",
                        "content": entry["message"],
                        "timestamp": entry["timestamp"]
                    })
                    history.append({
                        "role": "assistant",
                        "content": entry["response"]["response"],
                        "timestamp": entry["timestamp"]
                    })
                    
                    if len(history) >= max_messages:
                        break
                        
            return history
            
        except Exception as e:
            raise ProcessingError(
                f"Failed to retrieve conversation history: {str(e)}",
                metadata=ErrorMetadata(
                    severity="error",
                    category="data_access",
                    context={
                        "conversation_id": conversation_id,
                        "component": "conversation_history"
                    }
                )
            )

    @with_error_handling({"component": "conversation_deletion"})
    async def delete_conversation(self, conversation_id: str):
        """
        Delete conversation history for GDPR compliance.
        
        Args:
            conversation_id: Unique identifier for the conversation to delete
        """
        try:
            log_file = self.conversation_storage_path / f"{conversation_id}.jsonl"
            
            if log_file.exists():
                log_file.unlink()
                
            # Log deletion for compliance
            deletion_log = self.conversation_storage_path / "deletions.log"
            async with aiofiles.open(deletion_log, 'a') as f:
                await f.write(
                    json.dumps({
                        "timestamp": datetime.utcnow().isoformat(),
                        "conversation_id": conversation_id,
                        "action": "deletion"
                    }) + '\n'
                )
                
        except Exception as e:
            raise ProcessingError(
                f"Failed to delete conversation: {str(e)}",
                metadata=ErrorMetadata(
                    severity="error",
                    category="data_deletion",
                    context={
                        "conversation_id": conversation_id,
                        "component": "conversation_deletion"
                    }
                )
            )

    @with_error_handling({"component": "health_check"})
    async def check_health(self) -> Dict[str, Any]:
        """
        Check the health status of the agent system.
        
        Returns:
            Dictionary containing health status information
        """
        try:
            return {
                "status": "healthy",
                "active_agents": list(self.supervisor.agents.keys()),
                "conversation_storage": str(self.conversation_storage_path),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise ProcessingError(
                f"Health check failed: {str(e)}",
                metadata=ErrorMetadata(
                    severity="warning",
                    category="health_check",
                    context={"component": "health_check"}
                )
            )

# Create singleton instance
agent_manager = AgentManager()