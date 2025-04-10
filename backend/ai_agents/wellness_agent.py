import json
import os
from typing import List, Dict, Any
from datetime import datetime, timezone
from .base_agent import BaseAgent, AgentOutput, ToolDefinition
from .rag_utils import SimpleRAGHelper

class WellnessAgent(BaseAgent):
    def __init__(self, name: str, model, tokenizer):
        super().__init__(name, model, tokenizer)
        self.priority = 2
        self.notifications = []
        self.rag_helper = SimpleRAGHelper(os.path.join('data', 'hotel_info', 'hotel_information.txt'))

    def should_handle(self, message: str) -> bool:
        keywords = ["wellness", "meditation", "yoga", "fitness", "spa", "relax", "massage", "facial", "sauna", "steam room"]
        return any(keyword in message.lower() for keyword in keywords)

    def process(self, message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        relevant_passages = self.rag_helper.get_relevant_passages(message)
        context = "\n".join([passage for passage, _ in relevant_passages])

        system_prompt = (
            "You are an AI assistant for hotel wellness services. "
            "Use the following context to answer the guest's question about spa and wellness services:\n"
            f"{context}\n"
            "Respond to guests politely and efficiently. "
            "Keep responses concise and professional."
        )

        response = self.generate_response(message, system_prompt)

        # Check if the spa is available based on the current time
        spa_available = self.check_spa_availability()

        # Create a notification for the booking
        notification = {
            "type": "wellness_booking",
            "service": self.extract_service_type(message),
            "availability": "available" if spa_available else "not available",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": self.name
        }
        self.notifications.append(notification)

        # Save the structured output to a log file
        self._save_to_log({
            "input": message,
            "response": response,
            "notification": notification,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": self.name
        })

        return self.format_output(response, [notification])

    def get_available_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition("book_session", "Book a wellness session or spa treatment")
        ]

    def handle_tool_call(self, tool_name: str, **kwargs) -> Any:
        if tool_name == "book_session":
            return self.book_session(**kwargs)
        else:
            return super().handle_tool_call(tool_name, **kwargs)

    def book_session(self, service_type: str, time: str) -> Dict[str, Any]:
        spa_available = self.check_spa_availability()
        if spa_available:
            booking_id = f"WB{datetime.now().strftime('%Y%m%d%H%M%S')}"
            return {
                "booking_id": booking_id,
                "status": "confirmed",
                "service_type": service_type,
                "time": time
            }
        else:
            return {
                "status": "unavailable",
                "message": "The spa is currently closed. Please check our opening hours."
            }

    def check_spa_availability(self) -> bool:
        spa_info = self.rag_helper.get_relevant_passages("Spa opening hours")[0][0]
        current_time = datetime.now().time()
        opening_time = datetime.strptime("9:00 AM", "%I:%M %p").time()
        closing_time = datetime.strptime("8:00 PM", "%I:%M %p").time()
        return opening_time <= current_time <= closing_time

    def extract_service_type(self, message: str) -> str:
        service_types = ["massage", "facial", "body treatment", "yoga", "meditation", "fitness"]
        for service in service_types:
            if service in message.lower():
                return service
        return "general wellness service"

    def get_keywords(self) -> List[str]:
        return ["wellness", "meditation", "yoga", "fitness", "spa", "relax", "massage", "facial", "sauna", "steam room"]

    def _save_to_log(self, data: Dict[str, Any]):
        log_dir = os.path.join("logs", "wellness")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"wellness_log_{datetime.now().strftime('%Y%m%d')}.json")
        
        with open(log_file, "a") as f:
            json.dump(data, f)
            f.write("\n")