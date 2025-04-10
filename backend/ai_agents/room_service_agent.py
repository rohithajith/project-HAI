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

    def process(self, message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        # Check if the message is about breakfast buffet
        if "breakfast buffet" in message.lower():
            relevant_passages = rag_helper.get_relevant_passages(message)
            context = "\n".join([passage for passage, _ in relevant_passages])
            
            system_prompt = (
                "You are an AI assistant for hotel room service. "
                "Use the following context to answer the guest's question about breakfast buffet:\n"
                f"{context}\n"
                "Respond to guests politely and efficiently. "
                "Keep responses concise and professional."
            )
        else:
            system_prompt = (
                "You are an AI assistant for hotel room service. "
                "Respond to guests politely and efficiently. "
                "Keep responses concise and professional."
            )

        response = self.generate_response(message, system_prompt)

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