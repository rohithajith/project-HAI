import json
import os
from typing import List, Dict, Any
from datetime import datetime, timezone
from .base_agent import BaseAgent, AgentOutput, ToolDefinition
from .rag_utils import rag_helper

class WellnessAgent(BaseAgent):
    def __init__(self, name: str, model, tokenizer):
        super().__init__(name, model, tokenizer)
        self.priority = 2
        self.notifications = []

    def should_handle(self, message: str) -> bool:
        keywords = ["wellness", "meditation", "yoga", "fitness", "spa", "relax", "massage", "facial", "sauna", "steam room"]
        return any(keyword in message.lower() for keyword in keywords)

    def process(self, message: str, memory) -> Dict[str, Any]:
        # Get only highly relevant lines with a higher threshold for spa/wellness queries
        relevant_lines = rag_helper.get_relevant_passages(message, min_score=0.5, k=5)
        
        # Only include context if we found relevant information
        if relevant_lines:
            # Format the relevant information in a clean, structured way
            formatted_context = ""
            for passage, score in relevant_lines:
                if score > 0.5:  # Only include highly relevant information
                    formatted_context += f"• {passage.strip()}\n"
            
            system_prompt = (
                "You are an AI assistant for hotel wellness services. "
                f"The guest has asked about: '{message}'\n"
                "Answer ONLY using these specific details:\n"
                f"{formatted_context}\n"
                "Be concise and professional. If you don't have enough information to fully "
                "answer their question, offer to connect them with our wellness team."
            )
        else:
            # No relevant information found, use a generic prompt
            system_prompt = (
                "You are an AI assistant for hotel wellness services. "
                "Respond to guests politely and efficiently regarding spa and wellness services. "
                "Keep responses concise and professional. "
                "Our hotel offers spa services including massages, facials, and wellness treatments. "
                "Offer to connect them with our wellness team for specific details."
            )

        response = self.generate_response(message, memory, system_prompt)

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
        # Get spa hours from the information
        spa_passages = rag_helper.get_relevant_passages("spa hours opening", min_score=0.4)
        
        # Default hours if not found in passages
        opening_time = datetime.strptime("9:00 AM", "%I:%M %p").time()
        closing_time = datetime.strptime("8:00 PM", "%I:%M %p").time()
        
        # Try to extract actual hours from passages
        if spa_passages:
            for passage, _ in spa_passages:
                if "spa:" in passage.lower() and "open" in passage.lower():
                    # Try to extract hours from the passage
                    try:
                        hours_text = passage.lower().split("open")[1].split("\n")[0].strip()
                        if "-" in hours_text:
                            hours = hours_text.split("-")
                            opening_str = hours[0].strip()
                            closing_str = hours[1].strip()
                            
                            # Parse times
                            if "am" in opening_str or "pm" in opening_str:
                                opening_time = datetime.strptime(opening_str, "%I:%M %p").time()
                            if "am" in closing_str or "pm" in closing_str:
                                closing_time = datetime.strptime(closing_str, "%I:%M %p").time()
                    except:
                        # If parsing fails, use defaults
                        pass
        
        current_time = datetime.now().time()
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