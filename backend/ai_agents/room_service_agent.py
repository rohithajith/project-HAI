import json
import os
from typing import List, Dict, Any
from .base_agent import BaseAgent, AgentOutput, ToolDefinition
from datetime import datetime, timezone
from .rag_utils import rag_helper

class RoomServiceAgent(BaseAgent):
    def __init__(self, name: str, model, tokenizer):
        super().__init__(name, model, tokenizer)
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
            
            system_prompt = (
                "You are an AI assistant for hotel room service. "
                f"The guest has asked about: '{message}'\n"
                "Answer ONLY using these specific details:\n"
                f"{formatted_context}\n"
                "Be concise and professional. If you don't have enough information to fully "
                "answer their question, offer to connect them with our room service team."
            )
        else:
            # No relevant information found, use a generic prompt
            system_prompt = (
                "You are an AI assistant for hotel room service. "
                "Respond to guests politely and efficiently. "
                "Keep responses concise and professional. "
                "Our hotel offers 24/7 room service with a variety of food and beverage options. "
                "Offer to connect them with our room service team for specific menu items and details."
            )

        response = self.generate_response(message, memory, system_prompt)

        # Check for specific requests and create tool calls
        tool_calls = []
        if "towel" in message.lower():
            tool_calls.append({
                "type": "towel_request",
                "request_type": "towels",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent": self.name
            })
        elif any(food in message.lower() for food in ["food", "burger", "fries"]):
            tool_calls.append({
                "type": "food_order",
                "request_type": "food",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent": self.name
            })

        # Add notifications
        self.notifications.extend(tool_calls)

        # Save the structured output to a log file
        self._save_to_log({
            "input": message,
            "response": response,
            "tool_calls": tool_calls,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": self.name
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
            return True
        elif tool_name == "place_order":
            # Implement order placement logic here
            return {"order_id": "12345", "status": "placed"}
        else:
            return super().handle_tool_call(tool_name, **kwargs)

    def get_keywords(self) -> List[str]:
        return ["room service", "food", "drink", "towel", "order", "burger", "fries", "breakfast", "buffet"]

    def _save_to_log(self, data: Dict[str, Any]):
        log_dir = os.path.join("logs", "room_service")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"room_service_log_{datetime.now().strftime('%Y%m%d')}.json")
        
        with open(log_file, "a") as f:
            json.dump(data, f)
            f.write("\n")