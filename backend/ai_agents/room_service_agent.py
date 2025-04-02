from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from .base_agent import BaseAgent, AgentOutput, ToolDefinition, ToolParameters, ToolParameterProperty

class RoomServiceOrder(BaseModel):
    """Schema for room service orders."""
    room_number: str = Field(..., description="Room number for delivery")
    items: List[Dict[str, Any]] = Field(..., description="List of ordered items")
    special_instructions: Optional[str] = Field(None, description="Special delivery instructions")
    delivery_time: Optional[datetime] = Field(None, description="Requested delivery time")
    dietary_restrictions: Optional[List[str]] = Field(None, description="Dietary restrictions or allergies")

class RoomServiceAgent(BaseAgent):
    """Agent responsible for handling room service requests."""
    
    def __init__(self):
        self.name = "room_service_agent"
        self.priority = 8  # Medium-high priority for guest comfort
        
        # Define available tools
        self.tools = [
            ToolDefinition(
                name="check_menu_availability",
                description="Check if menu items are currently available",
                parameters=ToolParameters(
                    type="object",
                    properties={
                        "item_ids": ToolParameterProperty(
                            type="array",
                            description="List of menu item IDs to check"
                        ),
                        "time": ToolParameterProperty(
                            type="string",
                            description="Time to check availability for"
                        )
                    },
                    required=["item_ids"]
                )
            ),
            ToolDefinition(
                name="place_order",
                description="Place a room service order",
                parameters=ToolParameters(
                    type="object",
                    properties={
                        "room_number": ToolParameterProperty(
                            type="string",
                            description="Room number for delivery"
                        ),
                        "order_items": ToolParameterProperty(
                            type="array",
                            description="List of items to order"
                        ),
                        "special_instructions": ToolParameterProperty(
                            type="string",
                            description="Special delivery instructions"
                        )
                    },
                    required=["room_number", "order_items"]
                )
            )
        ]

    def should_handle(self, message: str, history: List[Dict[str, Any]]) -> bool:
        """Determine if this agent should handle the message."""
        room_service_keywords = [
            "room service", "food", "drink", "breakfast", "lunch", "dinner",
            "menu", "order", "hungry", "thirsty", "meal", "snack",
            "bring to room", "delivery", "towel", "towels", "housekeeping",
            "clean", "amenities", "supplies"
        ]
        
        message_lower = message.lower()
        
        # Check for room service keywords
        has_keywords = any(keyword in message_lower for keyword in room_service_keywords)
        
        # Check if we're in an ongoing room service conversation
        in_conversation = self._is_in_room_service_conversation(history)
        
        return has_keywords or in_conversation

    async def process(self, message: str, history: List[Dict[str, Any]]) -> AgentOutput:
        """Process room service related requests."""
        # Content filtering
        if self._contains_harmful_content(message):
            return AgentOutput(
                response="I apologize, but I cannot process messages containing inappropriate "
                        "content. How else may I assist you with room service?"
            )

        # Extract room number
        room_number = self._extract_room_number(history)
        
        if not room_number:
            return AgentOutput(
                response="To help you with room service, could you please provide your room number?"
            )

        # Determine the type of request
        if self._is_menu_request(message):
            return await self._handle_menu_request(room_number)
        elif self._is_order_request(message):
            return await self._handle_order_request(message, room_number)
        elif self._is_status_request(message):
            return await self._handle_status_request(room_number)
        else:
            return await self._handle_general_inquiry(message, room_number)

    def _contains_harmful_content(self, message: str) -> bool:
        """Check for harmful or inappropriate content."""
        harmful_keywords = [
            "lgbtq", "rape", "bomb", "terror", "politics",
            "weapon", "drugs", "explicit", "offensive"
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in harmful_keywords)

    def _is_in_room_service_conversation(self, history: List[Dict[str, Any]]) -> bool:
        """Check if we're in an ongoing room service conversation."""
        if not history:
            return False
            
        # Check last few messages for room service context
        recent_history = history[-3:]  # Look at last 3 messages
        for entry in recent_history:
            if entry.get('agent') == self.name:
                return True
        return False

    def _is_menu_request(self, message: str) -> bool:
        """Check if the message is requesting the menu."""
        menu_keywords = ["menu", "what do you have", "what's available", "can i see"]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in menu_keywords)

    def _is_order_request(self, message: str) -> bool:
        """Check if the message is placing an order."""
        order_keywords = ["order", "bring", "i want", "i would like", "can i get"]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in order_keywords)

    def _is_status_request(self, message: str) -> bool:
        """Check if the message is requesting order status."""
        status_keywords = ["status", "where is", "how long", "when will"]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in status_keywords)

    async def _handle_menu_request(self, room_number: str) -> AgentOutput:
        """Handle requests to see the menu."""
        return AgentOutput(
            response="Here's our current room service menu. All prices are in USD and "
                    "include service charge and taxes:\n\n"
                    "🍳 BREAKFAST (6:00 AM - 11:00 AM)\n"
                    "- Continental Breakfast: $25\n"
                    "- American Breakfast: $30\n"
                    "- Healthy Start: $28\n\n"
                    "🍽️ ALL DAY DINING (11:00 AM - 10:00 PM)\n"
                    "- Club Sandwich: $22\n"
                    "- Caesar Salad: $18\n"
                    "- Burger & Fries: $25\n\n"
                    "Would you like to place an order?",
            notifications=[{
                "type": "menu_viewed",
                "room_number": room_number,
                "timestamp": datetime.utcnow().isoformat()
            }]
        )

    async def _handle_order_request(self, message: str, room_number: str) -> AgentOutput:
        """Handle food order requests."""
        # TODO: Implement order parsing and validation
        return AgentOutput(
            response="I'll help you place your order. To ensure accuracy, please confirm:\n"
                    "1. The items you'd like to order\n"
                    "2. Any special instructions (allergies, preferences)\n"
                    "3. Preferred delivery time (if not ASAP)\n\n"
                    "You can say something like 'I'd like a Club Sandwich and Caesar Salad "
                    "delivered at 2 PM, no onions please.'",
            notifications=[{
                "type": "order_started",
                "room_number": room_number,
                "timestamp": datetime.utcnow().isoformat()
            }]
        )

    async def _handle_status_request(self, room_number: str) -> AgentOutput:
        """Handle order status inquiries."""
        # TODO: Implement order status checking
        return AgentOutput(
            response="Let me check the status of your order. One moment please...",
            notifications=[{
                "type": "status_check",
                "room_number": room_number,
                "timestamp": datetime.utcnow().isoformat()
            }]
        )

    async def _handle_general_inquiry(self, message: str, room_number: str) -> AgentOutput:
        """Handle general room service and housekeeping inquiries."""
        # Check for towel request
        if "towel" in message.lower():
            return AgentOutput(
                response="I'll arrange to have fresh towels delivered to your room right away. "
                        "Is there anything specific you need (bath towels, hand towels, etc.)?",
                notifications=[{
                    "type": "housekeeping_request",
                    "request_type": "towels",
                    "room_number": room_number,
                    "timestamp": datetime.utcnow().isoformat()
                }]
            )
        
        # Default response for other inquiries
        return AgentOutput(
            response="I can help you with room service orders, housekeeping items, or checking "
                    "your request status. Would you like to:\n"
                    "1. See our menu?\n"
                    "2. Place an order?\n"
                    "3. Request housekeeping items?\n"
                    "4. Check request status?",
            notifications=[{
                "type": "general_inquiry",
                "room_number": room_number,
                "timestamp": datetime.utcnow().isoformat()
            }]
        )