"""
aim of the agent: Manages wellness services like spa and meditation.
inputs of agent: User message, service type.
output json of the agent: Service availability or booking status.
method: Checks schedules and confirms bookings.
"""
import json
import os
import re
from typing import List, Dict, Any
from datetime import datetime, timezone
from .base_agent import BaseAgent, AgentOutput, ToolDefinition
from .rag_utils import rag_helper
from langchain.tools import tool

class WellnessAgent(BaseAgent):
    def __init__(self, name: str, model, tokenizer):
        super().__init__(name, model, tokenizer)
        # Use the correct path for the description file
        self.description = self.load_prompt("backend/ai_agents/descriptions/wellness_agent_description.txt")
        # Use the correct path for the prompt file
        self.system_prompt = self.load_prompt("wellness_agent_prompt.txt")
        self.priority = 2
        self.notifications = []

    def should_handle(self, message: str) -> bool:
        keywords = ["wellness", "meditation", "yoga", "fitness", "spa", "relax", "massage", "facial", "sauna", "steam room"]
        return any(keyword in message.lower() for keyword in keywords)

    def process(self, message: str, memory) -> Dict[str, Any]:
        # Get only highly relevant lines with a higher threshold for spa/wellness queries
        relevant_lines = rag_helper.get_relevant_passages(message, min_score=0.5, k=5)
        
        # Check if the query is specifically about spa timings
        is_spa_timing_query = any(keyword in message.lower() for keyword in ["spa time", "spa hours", "spa opening", "spa timing"])
        
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
        elif is_spa_timing_query:
            # Specific handling for spa timing queries with no RAG results
            system_prompt = (
                "You are an AI assistant for hotel wellness services. "
                "The guest has asked about spa timings, but no specific information was found. "
                "Respond with a message indicating that the exact spa timings could not be retrieved. "
                "Suggest that the guest contact the front desk or wellness team directly for the most up-to-date information."
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

        # Prepare tool calls
        tool_calls = []
        service_type = self.extract_service_type(message)
        
        # Check if the request is for booking a service
        if any(keyword in message.lower() for keyword in ["book", "reserve", "schedule"]):
            tool_calls.append({
                "tool_name": "book_session",
                "parameters": {
                    "service_type": service_type,
                    "time": self._extract_time(message)
                }
            })
        
        # If no specific tool calls, add a generic check availability call
        if not tool_calls:
            tool_calls.append({
                "tool_name": "check_service_availability",
                "parameters": {
                    "service_type": service_type
                }
            })

        # Check if the spa is available based on the current time
        spa_available = self.check_spa_availability()

        # Create a notification for the booking
        notification = {
            "type": "wellness_booking",
            "service": service_type,
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
            "tool_calls": tool_calls,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": self.name
        })

        return self.format_output(response, tool_calls)

    def get_available_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition("book_session", "Book a wellness session or spa treatment"),
            ToolDefinition("check_service_availability", "Check availability of wellness services")
        ]

    def get_keywords(self) -> List[str]:
        return ["wellness", "meditation", "yoga", "fitness", "spa", "relax", "massage", "facial", "sauna", "steam room"]

    def _save_to_log(self, data: Dict[str, Any]):
        log_dir = os.path.join("logs", "wellness")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"wellness_log_{datetime.now().strftime('%Y%m%d')}.jsonl")
        
        with open(log_file, "a") as f:
            json.dump(data, f)
            f.write("\n")

    @tool
    def check_service_availability(self, service_type: str = None) -> Dict[str, Any]:
        """
        Check availability of wellness services.
        
        Args:
            service_type (str, optional): Specific service to check. Defaults to None.
        
        Returns:
            Dict containing service availability details.
        """
        spa_available = self.check_spa_availability()
        available_services = self._get_available_services()
        
        if service_type:
            return {
                "service": service_type,
                "available": service_type.lower() in available_services and spa_available,
                "spa_status": "open" if spa_available else "closed"
            }
        
        return {
            "spa_available": spa_available,
            "available_services": available_services
        }

    @tool
    def book_session(self, service_type: str, time: str = None) -> Dict[str, Any]:
        """
        Book a wellness session.
        
        Args:
            service_type (str): Type of wellness service to book.
            time (str, optional): Preferred time for the session. Defaults to None.
        
        Returns:
            Dict containing booking details and status.
        """
        spa_available = self.check_spa_availability()
        if spa_available:
            booking_id = f"WB{datetime.now().strftime('%Y%m%d%H%M%S')}"
            return {
                "booking_id": booking_id,
                "status": "confirmed",
                "service_type": service_type,
                "time": time or "next available slot"
            }
        else:
            return {
                "status": "unavailable",
                "message": "The spa is currently closed. Please check our opening hours."
            }

    def check_spa_availability(self) -> bool:
        """
        Check if the spa is currently available.
        
        Returns:
            bool: True if spa is open, False otherwise.
        """
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

    def _get_available_services(self) -> List[str]:
        """
        Get a list of available wellness services.
        
        Returns:
            List[str]: Available wellness services.
        """
        return ["massage", "facial", "body treatment", "yoga", "meditation", "fitness"]

    def extract_service_type(self, message: str) -> str:
        """
        Extract the type of wellness service from the message.
        
        Args:
            message (str): The input message.
        
        Returns:
            str: The extracted service type or a generic wellness service.
        """
        service_types = self._get_available_services()
        for service in service_types:
            if service in message.lower():
                return service
        return "general wellness service"

    def _extract_time(self, message: str) -> str:
        """
        Extract the time from the message.
        
        Args:
            message (str): The input message.
        
        Returns:
            str: The extracted time or "next available".
        """
        # Simple time extraction using regex
        time_match = re.search(r'\b(\d{1,2}(?:am|pm))\b', message.lower())
        return time_match.group(1) if time_match else "next available"