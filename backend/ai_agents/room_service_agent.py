import re
from typing import List, Dict, Any, Optional

from .base_agent import BaseAgent, ToolDefinition, ToolParameters, ToolParameterProperty, AgentOutput
# Assuming a similar notification service exists in Python
# from backend.services.notification_service import notification_service

# Placeholder for the notification service if not yet implemented
class MockNotificationService:
    async def send_room_notification(self, room_number: str, message: str):
        print(f"--- NOTIFICATION to Room {room_number}: {message} ---")
    async def send_system_notification(self, notification_data: Dict[str, Any]):
         print(f"--- SYSTEM NOTIFICATION: {notification_data} ---")

notification_service = MockNotificationService() # Replace with actual import when available


class RoomServiceAgent(BaseAgent):
    name: str = "RoomServiceAgent"
    priority: int = 1 # Same priority as MaintenanceAgent in JS, adjust if needed

    tools: List[ToolDefinition] = [
        ToolDefinition(
            name='order_food',
            description='Place food order from room service menu',
            parameters=ToolParameters(
                properties={
                    'items': ToolParameterProperty(
                        type='array',
                        description='List of food items to order (e.g., ["burger", "fries"])',
                        # Pydantic v2 doesn't directly support 'items' like JSON schema.
                        # We rely on description and LLM understanding or further validation.
                        # Example for LLM: items: List[str] = Field(..., description="List...")
                    ),
                    'special_instructions': ToolParameterProperty(
                        type='string',
                        description='Any special preparation instructions (e.g., "no onions")'
                    )
                },
                required=['items']
            )
        ),
        ToolDefinition(
            name='order_drinks',
            description='Place drink order from room service menu',
            parameters=ToolParameters(
                properties={
                    'beverages': ToolParameterProperty(
                        type='array',
                        description='List of beverages to order (e.g., ["coke", "water"])',
                        # Similar note as 'items' above for array type handling
                    ),
                    'ice_preference': ToolParameterProperty(
                        type='string',
                        description='Ice preference for drinks',
                        enum=['none', 'light', 'regular', 'extra'],
                        default='regular' # Added a default
                    )
                },
                required=['beverages']
            )
        )
    ]

    def should_handle(self, message: str, history: List[Dict[str, Any]]) -> bool:
        """Check if the message relates to room service (food/drinks)."""
        lower_message = message.lower()
        keywords = [
            'room service', 'food', 'drink', 'beverage', 'menu', 'order',
            'eat', 'hungry', 'thirsty', 'snack', 'meal'
        ]
        return any(keyword in lower_message for keyword in keywords)

    async def process(self, message: str, history: List[Dict[str, Any]]) -> AgentOutput:
        """
        Process a room service request using improved keyword matching.
        """
        lower_message = message.lower()
        room_number = self._extract_room_number(history) or 'unknown'
        selected_tool_name: Optional[str] = None
        tool_args: Dict[str, Any] = {}

        # More comprehensive keyword sets
        food_keywords = ['food', 'eat', 'hungry', 'snack', 'meal', 'menu', 'order', 'sandwich', 'burger', 'fries', 'pizza', 'breakfast', 'lunch', 'dinner']
        drink_keywords = ['drink', 'beverage', 'thirsty', 'coke', 'water', 'juice', 'soda', 'coffee', 'tea']

        # Check for keywords, giving priority to food if both types are mentioned
        is_food_request = any(k in lower_message for k in food_keywords)
        is_drink_request = any(k in lower_message for k in drink_keywords)

        if is_food_request:
            selected_tool_name = 'order_food'
            # Simplified arg extraction - LLM/parsing needed for real items
            # Extract potential items crudely for now
            potential_items = [word for word in message.split() if word.lower() in food_keywords or len(word) > 3] # Basic filter
            tool_args = {'items': potential_items or [message], 'special_instructions': ''} # Use message as fallback
            # logger.info(f"Selected tool 'order_food' with args: {tool_args}") # Add logging if needed

        elif is_drink_request:
            selected_tool_name = 'order_drinks'
            # Simplified arg extraction
            potential_drinks = [word for word in message.split() if word.lower() in drink_keywords or len(word) > 3]
            ice_pref = 'regular'
            if 'no ice' in lower_message: ice_pref = 'none'
            elif 'light ice' in lower_message: ice_pref = 'light'
            elif 'extra ice' in lower_message: ice_pref = 'extra'
            tool_args = {'beverages': potential_drinks or [message], 'ice_preference': ice_pref}
            # logger.info(f"Selected tool 'order_drinks' with args: {tool_args}") # Add logging if needed

        # Execute the selected tool if one was identified
        if selected_tool_name == 'order_food':
            return await self._handle_food_order(room_number, tool_args)
        elif selected_tool_name == 'order_drinks':
            return await self._handle_drink_order(room_number, tool_args)
        else:
            # If should_handle was true but process didn't select a tool, return non-handling output
            # This signals the agent manager to try the next agent or fallback
            return AgentOutput(response="", tool_used=False, notifications=[])

    async def _handle_food_order(self, room_number: str, args: Dict[str, Any]) -> AgentOutput:
        """Simulates placing a food order."""
        items = args.get('items', ['Unknown item'])
        instructions = args.get('special_instructions', 'None')
        items_str = ", ".join(items)

        await notification_service.send_room_notification(
            room_number,
            f"Food order placed: {items_str}. Instructions: {instructions}"
        )
        await notification_service.send_system_notification({
             'type': 'room_service_food',
             'roomNumber': room_number,
             'items': items,
             'instructions': instructions
        })

        response_message = f"Your food order ({items_str}) has been placed for room {room_number}. It should arrive in about 30 minutes."
        if instructions:
            response_message += f" Special instructions: {instructions}."

        return AgentOutput(
            response=response_message,
            notifications=[{
                'event': 'room_service_food', # Changed 'type' to 'event'
                'payload': {                  # Wrapped details in 'payload'
                    'roomNumber': room_number,
                    'items': items,
                    'instructions': instructions
                }
            }],
            tool_used=True,
            tool_name='order_food',
            tool_args=args
        )

    async def _handle_drink_order(self, room_number: str, args: Dict[str, Any]) -> AgentOutput:
        """Simulates placing a drink order."""
        beverages = args.get('beverages', ['Unknown beverage'])
        ice = args.get('ice_preference', 'regular')
        beverages_str = ", ".join(beverages)

        await notification_service.send_room_notification(
            room_number,
            f"Drink order placed: {beverages_str}. Ice: {ice}"
        )
        await notification_service.send_system_notification({
             'type': 'room_service_drink',
             'roomNumber': room_number,
             'beverages': beverages,
             'ice_preference': ice
        })

        response_message = f"Your drink order ({beverages_str}) has been placed for room {room_number} with {ice} ice. It should arrive in about 15 minutes."
        return AgentOutput(
            response=response_message,
            notifications=[{
                'event': 'room_service_drink', # Changed 'type' to 'event'
                'payload': {                   # Wrapped details in 'payload'
                    'roomNumber': room_number,
                    'beverages': beverages,
                    'ice_preference': ice
                }
            }],
            tool_used=True,
            tool_name='order_drinks',
            tool_args=args
        )

# Example usage (for testing purposes)
if __name__ == '__main__':
    import asyncio

    async def test():
        agent = RoomServiceAgent()
        history = [{'role': 'user', 'content': 'I am in room 205.'}]
        message1 = "I'm hungry, can I order a club sandwich and fries?"
        message2 = "I'd like to get a coke with light ice and a bottle of water."
        message3 = "What's on the room service menu?" # Should trigger food tool by current logic

        print("Available tools:", agent.get_available_tools())

        print(f"\nTesting message 1: '{message1}'")
        if agent.should_handle(message1, history):
            output1 = await agent.process(message1, history)
            print("Output 1:", output1)
        else:
            print("Agent decided not to handle message 1.")

        print(f"\nTesting message 2: '{message2}'")
        if agent.should_handle(message2, history):
            output2 = await agent.process(message2, history)
            print("Output 2:", output2)
        else:
            print("Agent decided not to handle message 2.")

        print(f"\nTesting message 3: '{message3}'")
        if agent.should_handle(message3, history):
            output3 = await agent.process(message3, history)
            print("Output 3:", output3)
        else:
            print("Agent decided not to handle message 3.")


    asyncio.run(test())