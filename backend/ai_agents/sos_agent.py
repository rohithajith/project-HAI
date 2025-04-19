"""
aim of the agent: Handles emergency SOS requests.
inputs of agent: User message, emergency type.
output json of the agent: Emergency alert and notification status.
method: Triggers immediate staff notification.
"""
from typing import List, Dict, Any
from .base_agent import BaseAgent
import json
from datetime import datetime, timezone

class SOSAgent(BaseAgent):
    def should_handle(self, message: str) -> bool:
        """
        Determine if the message is an SOS emergency
        """
        sos_keywords = [
            "fire", "emergency", "help", "panic attack", 
            "medical help", "urgent", "danger", "hurt", 
            "bleeding", "choking", "unconscious", 
            "need assistance", "sos", "critical"
        ]
        return any(keyword in message.lower() for keyword in sos_keywords)

    def process(self, message: str, memory) -> Dict[str, Any]:
        """
        Process SOS emergency requests
        """
        # Detect specific emergency type
        emergency_type = self._detect_emergency_type(message)
        
        # Prepare emergency metadata
        emergency_metadata = {
            "type": emergency_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "guest_message": message,
            "priority": "CRITICAL"
        }
        
        # Prepare response
        response_text = (
            "EMERGENCY ALERT: Our staff has been notified and will respond immediately. "
            "Please stay calm and follow any immediate safety instructions. "
            "Help is on the way."
        )
        
        # Tool call to notify admin dashboard
        tool_calls = [{
            "tool_name": "notify_admin_dashboard",
            "arguments": {
                "emergency_details": json.dumps(emergency_metadata)
            }
        }]
        
        return self.format_output(response_text, tool_calls)
    
    def _detect_emergency_type(self, message: str) -> str:
        """
        Detect specific type of emergency based on message content
        """
        message_lower = message.lower()
        
        if "fire" in message_lower:
            return "FIRE"
        elif "panic attack" in message_lower:
            return "MEDICAL_MENTAL_HEALTH"
        elif any(keyword in message_lower for keyword in ["medical help", "bleeding", "hurt", "choking", "unconscious"]):
            return "MEDICAL_EMERGENCY"
        elif "danger" in message_lower:
            return "PERSONAL_SAFETY"
        else:
            return "GENERAL_EMERGENCY"