import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List, Dict, Any, Tuple
import re
from .base_agent import BaseAgent
from .supervisor_agent import SupervisorAgent
from .room_service_agent import RoomServiceAgent
from .maintenance_agent import MaintenanceAgent
from .wellness_agent import WellnessAgent
from .conversation_memory import ConversationMemory
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
        
        # Initialize conversation memory
        self.memory = ConversationMemory()

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

    def filter_input(self, user_input: str) -> Tuple[str, bool]:
        """
        Filter user input to prevent offensive, political, or sensitive content.
        
        Args:
            user_input: The raw user input
            
        Returns:
            Tuple containing:
            - Filtered input (or original if no issues found)
            - Boolean indicating if content was filtered
        """
        # List of patterns to filter (can be expanded)
        offensive_patterns = [
            r'\b(hate|kill|murder|attack|bomb|terrorist|suicide)\b',
            r'\b(racist|sexist|homophobic|transphobic)\b',
            r'\b(nazi|hitler|genocide)\b',
            r'\b(f[*u]ck|sh[*i]t|b[*i]tch|c[*u]nt|a[*s]s|d[*i]ck)\b',
            r'\b(porn|nude|naked|sex|xxx)\b'
        ]
        
        political_patterns = [
            r'\b(democrat|republican|liberal|conservative|socialism|communism|fascism)\b',
            r'\b(trump|biden|obama|clinton|bush|election|vote|ballot)\b',
            r'\b(congress|senate|parliament|president|prime minister|politician)\b',
            r'\b(protest|riot|revolution|coup|insurrection)\b'
        ]
        
        sensitive_patterns = [
            r'\b(hack|exploit|vulnerability|bypass|crack|steal|fraud)\b',
            r'\b(credit card|social security|passport|identity theft)\b',
            r'\b(illegal|criminal|crime|drugs|cocaine|heroin|marijuana)\b',
            r'\b(weapon|gun|rifle|pistol|firearm|ammunition)\b'
        ]
        
        # Combine all patterns
        all_patterns = offensive_patterns + political_patterns + sensitive_patterns
        
        # Check if any pattern matches
        for pattern in all_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                # Content was filtered
                return self._get_safe_input_response(), True
        
        # No issues found, return original input
        return user_input, False
    
    def _get_safe_input_response(self) -> str:
        """
        Return a safe alternative to filtered user input.
        """
        return "I need assistance with a hotel-related matter."
    
    def _get_safe_output_response(self) -> Dict[str, Any]:
        """
        Return a safe alternative to filtered model output.
        """
        safe_response = "I apologize, but I'm not able to respond to that request. As a hotel assistant, I'm here to help with hotel-related inquiries, reservations, amenities, and local recommendations. How else may I assist you with your stay?"
        return {
            "response": safe_response,
            "tool_calls": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": "FilterAgent"
        }
    
    def process(self, message: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        # Filter user input first
        filtered_message, was_filtered = self.filter_input(message)
        
        # If input was filtered, return safe response directly
        if was_filtered:
            safe_response = self._get_safe_output_response()
            # Add filtered message to memory
            self.memory.add_message("user", filtered_message)
            # Add safe response to memory
            self.memory.add_message("assistant", safe_response["response"], "FilterAgent")
            return safe_response
        
        # Add user message to memory
        self.memory.add_message("user", message)
        
        # Fast path for room service requests
        room_service_keywords = ["towel", "food", "drink", "order", "burger", "fries"]
        if any(keyword in message.lower() for keyword in room_service_keywords):
            response = self.room_service_agent.process(message, self.memory)
            # Add assistant response to memory
            self.memory.add_message("assistant", response["response"], "RoomServiceAgent")
            return response

        # Fast path for maintenance requests
        maintenance_keywords = ["broken", "repair", "fix", "not working", "schedule maintenance"]
        if any(keyword in message.lower() for keyword in maintenance_keywords):
            response = self.maintenance_agent.process(message, self.memory)
            # Add assistant response to memory
            self.memory.add_message("assistant", response["response"], "MaintenanceAgent")
            return response

        # Fast path for wellness requests
        wellness_keywords = ["wellness", "spa", "massage", "yoga", "fitness", "relax", "meditation"]
        if any(keyword in message.lower() for keyword in wellness_keywords):
            response = self.wellness_agent.process(message, self.memory)
            # Add assistant response to memory
            self.memory.add_message("assistant", response["response"], "WellnessAgent")
            return response

        # Default path: use supervisor to route the request
        response = self.supervisor.process(message, self.memory)
        # Add assistant response to memory
        self.memory.add_message("assistant", response["response"], response["agent"])
        return response

    def handle_error(self, error: Exception) -> Dict[str, Any]:
        # Create error message
        error_message = f"An error occurred: {str(error)}"
        print(f"Error in AgentManager: {error_message}")
        
        # Filter the error message to ensure it doesn't contain sensitive information
        filtered_error, was_filtered = self.filter_input(error_message)
        
        if was_filtered:
            return self._get_safe_output_response()
        
        return {
            "response": "I apologize, but I encountered an error processing your request. Please try again or contact hotel staff for assistance.",
            "tool_calls": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": "ErrorHandler"
        }
        
    # Methods to manage conversations
    def start_new_conversation(self):
        """Start a new conversation"""
        self.memory = ConversationMemory()
        return self.memory.conversation_id
        
    def load_conversation(self, conversation_id):
        """Load a previous conversation"""
        return self.memory.load_conversation(conversation_id)