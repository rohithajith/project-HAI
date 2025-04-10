import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List, Dict, Any
from .base_agent import BaseAgent
from .supervisor_agent import SupervisorAgent
from .room_service_agent import RoomServiceAgent
from .maintenance_agent import MaintenanceAgent
from .wellness_agent import WellnessAgent
from datetime import datetime, timezone
import os
class AgentManager:
    def __init__(self):
        self.model, self.tokenizer = self.load_model()
        self.supervisor = SupervisorAgent("SupervisorAgent", self.model, self.tokenizer)
        self.room_service_agent = RoomServiceAgent("RoomServiceAgent", self.model, self.tokenizer)
        self.maintenance_agent = MaintenanceAgent("MaintenanceAgent", self.model, self.tokenizer)
        self.wellness_agent = WellnessAgent("WellnessAgent", self.model, self.tokenizer)
        
        self.supervisor.register_agent(self.room_service_agent)
        self.supervisor.register_agent(self.maintenance_agent)
        self.supervisor.register_agent(self.wellness_agent)

    def load_model(self):
        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'finetunedmodel-merged'))
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        print(f"Loading model from: {model_path}")

        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            trust_remote_code=True,
            load_in_8bit=True,  # Enable bitsandbytes quantization if needed
            device_map="auto"  # Automatically selects CUDA if available
        )

        print("✅ Model loaded successfully!")
        return model, tokenizer

    def process(self, message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        # Fast path for room service requests
        room_service_keywords = ["towel", "food", "drink", "order", "burger", "fries"]
        if any(keyword in message.lower() for keyword in room_service_keywords):
            return self.room_service_agent.process(message, history)

        # Fast path for maintenance requests
        maintenance_keywords = ["broken", "repair", "fix", "not working", "schedule maintenance"]
        if any(keyword in message.lower() for keyword in maintenance_keywords):
            return self.maintenance_agent.process(message, history)

        # Fast path for wellness requests
        wellness_keywords = ["wellness", "spa", "massage", "yoga", "fitness", "relax", "meditation"]
        if any(keyword in message.lower() for keyword in wellness_keywords):
            return self.wellness_agent.process(message, history)

        # Default path: use supervisor to route the request
        return self.supervisor.process(message, history)

    def handle_error(self, error: Exception) -> Dict[str, Any]:
        error_message = f"An error occurred: {str(error)}"
        print(f"Error in AgentManager: {error_message}")
        return {
            "response": error_message,
            "tool_calls": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": "ErrorHandler"
        }