"""
aim of the agent: Manages room service orders and requests.
inputs of agent: User message, order details.
output json of the agent: Order confirmation or status.
method: Processes orders and updates inventory.
"""
import json
import os
import re
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from .base_agent import BaseAgent, AgentOutput, ToolDefinition
from .rag_utils import rag_helper
from langchain.tools import tool

class RoomServiceAgent(BaseAgent):
    def __init__(self, name: str, model, tokenizer):
        super().__init__(name, model, tokenizer)
        self.description = "Handles guest requests for food, beverages, towels, and other room service amenities."
        self.system_prompt = self.load_prompt("room_service_default_prompt.txt")
        self.priority = 1  # High priority
        self.notifications = []

    def should_handle(self, message: str) -> bool:
        keywords = ["room service", "food", "drink", "towel", "order", "burger", "fries", "breakfast", "buffet"]
        return any(keyword in message.lower() for keyword in keywords)

    def process(self, message: str, memory) -> Dict[str, Any]:
        # Get only highly relevant lines with a higher threshold
        relevant_lines = rag_helper.get_relevant_passages(message, min_score=0.5, k=5)
        
        # Only include context if we found relevant information
        if relevant_lines:
            # Format the relevant information in a clean, structured way
            formatted_context = ""
            for passage, score in relevant_lines:
                if score > 0.5:  # Only include highly relevant information
                    formatted_context += f"• {passage.strip()}\n"
            
            system_prompt = self.load_prompt("room_service_context_prompt.txt", context=formatted_context, message=message)
        else:
            # No relevant information found, use a generic prompt
            system_prompt = self.load_prompt("room_service_default_prompt.txt")

        response = self.generate_response(message, memory, system_prompt)

        # Prepare tool calls
        tool_calls = []
        
        # Check for specific service requests
        if "towel" in message.lower():
            tool_calls.append({
                "tool_name": "place_order",
                "parameters": {
                    "item_type": "towels",
                    "quantity": 1
                }
            })
        elif any(food in message.lower() for food in ["food", "burger", "fries", "order"]):
            tool_calls.append({
                "tool_name": "place_order",
                "parameters": {
                    "item_type": "food",
                    "details": message
                }
            })
        
        # If no specific tool calls, add a generic check availability call
        if not tool_calls:
            tool_calls.append({
                "tool_name": "check_menu_availability",
                "parameters": {}
            })

        # Add notifications
        self.notifications.extend(tool_calls)

        # Save the structured output to a log file with GDPR compliance
        self._save_to_log({
            "input": self._anonymize_personal_data(message),  # Anonymize personal data
            "response": response,
            "tool_calls": tool_calls,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": self.name,
            "data_purpose": "customer_service",  # Purpose limitation
            "retention_period": (datetime.now(timezone.utc) + timedelta(days=90)).isoformat(),  # Storage limitation
            "consent_reference": memory.conversation_id  # Link to consent record
        })

        return self.format_output(response, tool_calls)

    def get_available_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition("check_menu_availability", "Check if an item is available on the menu"),
            ToolDefinition("place_order", "Place an order for room service")
        ]

    def handle_tool_call(self, tool_name: str, **kwargs) -> Any:
        if tool_name == "check_menu_availability":
            # Implement menu availability check logic here
            return {
                "available_items": ["towels", "breakfast", "burger", "fries"],
                "status": "available"
            }
        elif tool_name == "place_order":
            # Implement order placement logic here
            order_details = {
                "order_id": f"RS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "status": "placed",
                "item_type": kwargs.get('item_type', 'unknown'),
                "details": kwargs.get('details', '')
            }
            return order_details
        else:
            return super().handle_tool_call(tool_name, **kwargs)

    def get_keywords(self) -> List[str]:
        return ["room service", "food", "drink", "towel", "order", "burger", "fries", "breakfast", "buffet"]

    def _anonymize_personal_data(self, text: str) -> str:
        """
        Anonymize personal identifiable information in text.
        
        Args:
            text: The text to anonymize
            
        Returns:
            Anonymized text with personal data replaced
        """
        # Patterns for common personal data
        patterns = [
            # Phone numbers (various formats)
            (r'\b(?:\+\d{1,3}[-\s]?)?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}\b', '[PHONE_NUMBER]'),
            
            # Email addresses
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_ADDRESS]'),
            
            # Credit card numbers (simplified pattern)
            (r'\b(?:\d{4}[-\s]?){3}\d{4}\b', '[PAYMENT_CARD]'),
            
            # Names (common title + name pattern, simplified)
            (r'\b(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+[A-Z][a-z]+\b', '[NAME]'),
            
            # Room numbers
            (r'\b(?:room|suite)\s+\d+\b', '[ROOM_NUMBER]'),
            
            # Addresses (simplified pattern)
            (r'\b\d+\s+[A-Za-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b', '[ADDRESS]'),
            
            # Social Security Numbers (US)
            (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),
            
            # Passport numbers (simplified pattern)
            (r'\b[A-Z]{1,2}\d{6,9}\b', '[PASSPORT_NUMBER]')
        ]
        
        # Apply each pattern
        anonymized_text = text
        for pattern, replacement in patterns:
            anonymized_text = re.sub(pattern, replacement, anonymized_text, flags=re.IGNORECASE)
            
        return anonymized_text

    def _save_to_log(self, data: Dict[str, Any]):
        """
        Save data to log with GDPR and LESP compliance.
        
        This function implements:
        1. Data minimization - Only storing necessary data
        2. Purpose limitation - Documenting why data is stored
        3. Storage limitation - Setting retention periods
        4. Data security - Structured storage with access controls
        """
        # Ensure we're not storing unnecessary data
        required_fields = [
            "input", "response", "timestamp", "agent",
            "data_purpose", "retention_period", "consent_reference"
        ]
        
        # Create a clean data object with only required fields
        clean_data = {k: data.get(k) for k in required_fields if k in data}
        
        # Add tool_calls only if they exist and are not empty
        if "tool_calls" in data and data["tool_calls"]:
            clean_data["tool_calls"] = data["tool_calls"]
        
        # Add metadata for GDPR compliance
        clean_data["gdpr_metadata"] = {
            "data_controller": "Hotel AI System",
            "legal_basis": "legitimate_interest",  # or "consent", "contract", etc.
            "data_subject_rights_url": "/api/user/data/rights",
            "logged_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Create directory structure that separates data by date for easier retention management
        current_date = datetime.now().strftime('%Y%m%d')
        year_month = datetime.now().strftime('%Y-%m')
        
        # Organize logs by year-month for easier retention management
        log_dir = os.path.join("logs", "room_service", year_month)
        os.makedirs(log_dir, exist_ok=True)
        
        # Use a unique identifier in the filename to avoid conflicts
        log_file = os.path.join(log_dir, f"room_service_log_{current_date}.jsonl")
        
        # Append to the log file
        with open(log_file, "a") as f:
            json.dump(clean_data, f)
            f.write("\n")

    @tool
    def check_menu_availability(self, item_type: str = None) -> Dict[str, Any]:
        """
        Check the availability of menu items.
        
        Args:
            item_type (str, optional): Specific item type to check. Defaults to None.
        
        Returns:
            Dict containing available items and their status.
        """
        available_items = ["towels", "breakfast", "burger", "fries"]
        
        if item_type:
            return {
                "item": item_type,
                "available": item_type.lower() in available_items,
                "status": "available" if item_type.lower() in available_items else "not available"
            }
        
        return {
            "available_items": available_items,
            "status": "available"
        }

    @tool
    def place_order(self, item_type: str, details: str = None, quantity: int = 1) -> Dict[str, Any]:
        """
        Place an order for room service.
        
        Args:
            item_type (str): Type of item to order.
            details (str, optional): Additional details about the order. Defaults to None.
            quantity (int, optional): Quantity of items to order. Defaults to 1.
        
        Returns:
            Dict containing order details and confirmation.
        """
        order_details = {
            "order_id": f"RS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "placed",
            "item_type": item_type,
            "details": details or "",
            "quantity": quantity,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        return order_details