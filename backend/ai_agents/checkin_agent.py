"""
aim of the agent: Manages guest check-ins and booking confirmations.
inputs of agent: User message, booking ID.
output json of the agent: Check-in confirmation or error details.
method: Validates booking ID and processes check-in.
"""
from typing import List, Dict, Any
import sqlite3
import os
import re
from datetime import datetime, timedelta
from .base_agent import BaseAgent
from langchain.tools import tool

class CheckInAgent(BaseAgent):
    def __init__(self, name: str, model, tokenizer):
        super().__init__(name, model, tokenizer)
        self.description = self.load_prompt("backend/ai_agents/descriptions/checkin_agent_description.txt")
        self.system_prompt = self.load_prompt("backend/ai_agents/prompts/checkin_agent_prompt.txt")
        self.db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'hotel_bookings.db')
        self.priority = 5  # Medium priority

    def get_keywords(self) -> List[str]:
        return [
            'check-in', 'checkin', 'booking', 
            'reservation', 'book', 'confirm booking',
            'extend stay', 'stay longer', 'extra night'
        ]

    def should_handle(self, message: str) -> bool:
        # More flexible handling of check-in and stay extension related messages
        check_in_patterns = [
            r'\b(check\s*-?\s*in)\b', 
            r'\b(booking)\b', 
            r'\b(reservation)\b', 
            r'\b(confirm)\s*(booking)?\b',
            r'\b(extend\s*stay)\b',
            r'\b(stay\s*longer)\b',
            r'\b(extra\s*night)\b'
        ]
        
        return any(re.search(pattern, message.lower()) for pattern in check_in_patterns)

    @tool
    def query_booking(self, booking_id: str) -> Dict[str, Any]:
        """
        Query booking details from SQLite database.
        
        Args:
            booking_id (str): The unique identifier for the booking.
        
        Returns:
            Dict[str, Any]: Booking details if found, None otherwise.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bookings WHERE booking_id = ?", (booking_id,))
            columns = [column[0] for column in cursor.description]
            result = cursor.fetchone()
            conn.close()

            if result:
                return dict(zip(columns, result))
            return None
        except Exception as e:
            print(f"Database query error: {e}")
            return None

    @tool
    def check_room_availability(self, room_type: str, check_out_date: str) -> bool:
        """
        Check if the same room type is available for the next day.
        
        Args:
            room_type (str): The type of room to check.
            check_out_date (str): The current booking's check-out date.
        
        Returns:
            bool: True if the room is available, False otherwise.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert check_out_date to datetime and add one day
            next_day = (datetime.strptime(check_out_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            
            # Check if the room type is available
            cursor.execute("""
                SELECT COUNT(*) 
                FROM bookings 
                WHERE room_type = ? 
                AND (
                    (check_in <= ? AND check_out > ?) OR
                    (check_in < ? AND check_out >= ?)
                )
            """, (room_type, next_day, next_day, next_day, next_day))
            
            available_rooms = cursor.fetchone()[0]
            conn.close()
            
            # If no bookings conflict, the room is available
            return available_rooms == 0
        except Exception as e:
            print(f"Room availability check error: {e}")
            return False

    @tool
    def extract_booking_id(self, message: str) -> str:
        """
        Extract booking ID from message using regex.
        
        Args:
            message (str): The input message to search for a booking ID.
        
        Returns:
            str: The extracted booking ID, or None if not found.
        """
        # Look for numeric booking IDs, prioritizing 4-digit numbers
        match = re.search(r'\b(\d{4})\b', message)
        return match.group(1) if match else None

    def process(self, message: str, memory) -> Dict[str, Any]:
        # Check if the message is about extending stay
        if re.search(r'\b(extend\s*stay|stay\s*longer|extra\s*night)\b', message.lower()):
            return self._handle_extend_stay(message)

        # Extract booking ID from message
        booking_id = self.extract_booking_id(message)
        
        if not booking_id:
            return self.format_output(
                "I couldn't find a booking ID in your message. Could you please provide your booking ID?",
                agent_name="CheckInAgent"
            )

        # Query booking details
        booking = self.query_booking(booking_id)
        
        if not booking:
            return self.format_output(
                f"Sorry, I couldn't find a booking with ID {booking_id}. Please check the booking number and try again.",
                agent_name="CheckInAgent"
            )

        # Prepare check-in confirmation message
        confirmation_message = (
            f"Check-in Approved for Booking #{booking_id}\n"
            f"Guest: {booking.get('guest_name', 'N/A')}\n"
            f"Room Type: {booking.get('room_type', 'N/A')}\n"
            f"Check-in: {booking.get('check_in', 'N/A')}\n"
            f"Check-out: {booking.get('check_out', 'N/A')}"
        )

        return self.format_output(
            confirmation_message,
            agent_name="CheckInAgent"
        )

    def _handle_extend_stay(self, message: str) -> Dict[str, Any]:
        """Handle stay extension request"""
        # Extract booking ID if provided
        booking_id = self.extract_booking_id(message)
        
        if not booking_id:
            return self.format_output(
                "To extend your stay, please provide your booking ID.",
                agent_name="CheckInAgent"
            )

        # Query booking details
        booking = self.query_booking(booking_id)
        
        if not booking:
            return self.format_output(
                f"Sorry, I couldn't find a booking with ID {booking_id}. Please check the booking number and try again.",
                agent_name="CheckInAgent"
            )

        # Check room availability for the next day
        room_type = booking.get('room_type')
        check_out_date = booking.get('check_out')
        
        if self.check_room_availability(room_type, check_out_date):
            return self.format_output(
                f"Great news! The {room_type} is available for an extra night. "
                "Would you like to extend your stay? Please confirm, and our staff will help you process the extension.",
                agent_name="CheckInAgent"
            )
        else:
            return self.format_output(
                f"I'm sorry, but the {room_type} is not available for an extra night. "
                "We can help you find alternative accommodation or room types if you'd like.",
                agent_name="CheckInAgent"
            )