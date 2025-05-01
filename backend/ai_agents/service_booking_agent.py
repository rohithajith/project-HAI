from typing import List, Dict, Any
import os
import re
"""
aim of the agent: Manages service bookings like spa and gym sessions.
inputs of agent: User message, service type, time slot.
output json of the agent: Booking confirmation or availability status.
method: Checks availability and confirms bookings.
"""
import json
from datetime import datetime, timedelta
from .base_agent import BaseAgent, ToolDefinition
from .rag_utils import rag_helper
from langchain.tools import tool

class ServiceBookingAgent(BaseAgent):
    def __init__(self, name: str, model, tokenizer):
        super().__init__(name, model, tokenizer)
        self.description = self.load_prompt("backend/ai_agents/descriptions/service_booking_agent_description.txt")
        self.system_prompt = self.load_prompt("backend/ai_agents/prompts/service_booking_agent_prompt.txt")
        self.priority = 6  # High priority for service bookings
        self.hotel_info_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'hotel_info', 'hotel_information.txt')
        self.hotel_policy_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'hotel_info', 'hotel_policies.txt')
        
        # Predefined services with their availability slots
        self.services = {
            'spa': {
                'available_slots': ['9am', '10am', '11am', '2pm', '3pm', '4pm'],
                'duration': 60,  # minutes
                'max_capacity': 5
            },
            'gym': {
                'available_slots': ['6am', '7am', '8am', '12pm', '5pm', '6pm', '7pm'],
                'duration': 90,  # minutes
                'max_capacity': 10
            },
            'meditation room': {
                'available_slots': ['8am', '10am', '12pm', '3pm', '5pm'],
                'duration': 45,  # minutes
                'max_capacity': 3
            }
        }

    def get_keywords(self) -> List[str]:
        return [
            'spa', 'gym', 'meditation', 'book service', 
            'wellness', 'book room', 'session'
        ]

    def get_available_tools(self) -> List[ToolDefinition]:
        """Define available tools for the ServiceBookingAgent"""
        return [
            ToolDefinition(
                name="check_menu_availability", 
                description="Check availability of a specific service or time slot"
            ),
            ToolDefinition(
                name="place_order", 
                description="Book a specific service at a given time"
            )
        ]

    def should_handle(self, message: str) -> bool:
        # Check if message contains any service-related keywords
        service_patterns = [
            r'\b(spa)\b', r'\b(gym)\b', r'\b(meditation)\b', 
            r'\b(wellness)\b', r'\b(book)\s*(service|room|session)\b'
        ]
        return any(re.search(pattern, message.lower()) for pattern in service_patterns)

    def _get_hotel_context(self, query: str) -> str:
        """Use RAG to retrieve relevant hotel information"""
        try:
            # Read hotel information and policies
            with open(self.hotel_info_path, 'r') as f:
                hotel_info = f.read()
            with open(self.hotel_policy_path, 'r') as f:
                hotel_policies = f.read()
            
            # Combine and use RAG to get relevant passages
            combined_text = hotel_info + "\n\n" + hotel_policies
            relevant_passages = rag_helper.get_relevant_passages(query, combined_text, k=3)
            
            return "\n".join([passage for passage, _ in relevant_passages])
        except Exception as e:
            print(f"Error retrieving hotel context: {e}")
            return ""

    def process(self, message: str, memory) -> Dict[str, Any]:
        # Normalize message
        message = message.lower()

        # Check if user is asking about service availability
        availability_match = re.search(r'do\s*(?:you)?\s*have\s*(spa|gym|meditation\s*room)', message)
        if availability_match:
            service = availability_match.group(1)
            
            # Use RAG to generate a response about service availability
            hotel_context = self._get_hotel_context(message)
            
            system_prompt = (
                f"You are an AI hotel assistant. Provide information about the {service} service. "
                "Use the following hotel context to inform your response:\n"
                f"{hotel_context}"
            )
            
            availability_response = self.generate_response(message, memory, system_prompt)
            return self.format_output(availability_response, agent_name="ServiceBookingAgent")

        # Check for service booking
        booking_match = re.search(r'book\s*(?:a)?\s*(spa|gym|meditation\s*room)\s*(?:session)?\s*(?:for)?\s*(\d+(?:am|pm))', message)
        if booking_match:
            service = booking_match.group(1)
            time_slot = booking_match.group(2)

            # Check service availability
            if self._check_service_availability(service, time_slot):
                # Generate booking confirmation with metadata
                booking_details = {
                    "service": service,
                    "time_slot": time_slot,
                    "duration": self.services[service]['duration'],
                    "booking_id": self._generate_booking_id(),
                    "timestamp": datetime.now().isoformat()
                }

                return {
                    "response": f"Your {service} session at {time_slot} has been booked successfully!",
                    "booking_details": booking_details,
                    "agent": "ServiceBookingAgent",
                    "tool_calls": [
                        {
                            "tool_name": "place_order",
                            "parameters": {
                                "service": service,
                                "time": time_slot
                            }
                        }
                    ]
                }
            else:
                return self.format_output(
                    f"Sorry, the {service} is not available at {time_slot}. "
                    f"Available slots are: {', '.join(self.services[service]['available_slots'])}",
                    agent_name="ServiceBookingAgent"
                )

        # Default response if no specific service request is found
        return self.format_output(
            "I can help you book services like spa, gym, or meditation room. "
            "What service would you like to book?",
            agent_name="ServiceBookingAgent"
        )

    def _generate_booking_id(self) -> str:
        """Generate a unique booking ID"""
        return f"SRV-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    @tool
    def check_menu_availability(self, service: str = None) -> Dict[str, Any]:
        """
        Check availability of services and their time slots.
        
        Args:
            service (str, optional): Specific service to check. Defaults to None.
        
        Returns:
            Dict containing service availability details.
        """
        if service and service.lower() in self.services:
            service_info = self.services[service.lower()]
            return {
                "service": service,
                "available_slots": service_info['available_slots'],
                "max_capacity": service_info['max_capacity'],
                "duration": service_info['duration']
            }
        
        # If no specific service or service not found, return all services
        return {
            "services": {
                service: {
                    "available_slots": details['available_slots'],
                    "max_capacity": details['max_capacity'],
                    "duration": details['duration']
                } for service, details in self.services.items()
            }
        }

    @tool
    def place_order(self, service: str, time: str) -> Dict[str, Any]:
        """
        Book a specific service at a given time.
        
        Args:
            service (str): The service to book.
            time (str): The time slot for the booking.
        
        Returns:
            Dict containing booking confirmation details.
        """
        # Check service availability
        if self._check_service_availability(service, time):
            booking_details = {
                "service": service,
                "time_slot": time,
                "duration": self.services[service.lower()]['duration'],
                "booking_id": self._generate_booking_id(),
                "status": "confirmed",
                "timestamp": datetime.now().isoformat()
            }
            return booking_details
        
        return {
            "status": "unavailable",
            "message": f"Sorry, the {service} is not available at {time}.",
            "available_slots": self.services.get(service.lower(), {}).get('available_slots', [])
        }

    def _check_service_availability(self, service: str, time_slot: str) -> bool:
        """
        Check if the requested service and time slot are available.
        
        Args:
            service (str): The service to check.
            time_slot (str): The time slot to check.
        
        Returns:
            bool: True if the service and time slot are available, False otherwise.
        """
        service = service.lower()
        if service not in self.services:
            return False
        
        return time_slot.lower() in self.services[service]['available_slots']