import asyncio
import pytest
from datetime import datetime
from ai_agents.room_service_agent import RoomServiceAgent
from ai_agents.base_agent import AgentOutput

class TestRoomServiceAgent:
    def setup_method(self):
        """Initialize the room service agent before each test."""
        self.agent = RoomServiceAgent()

    @pytest.mark.asyncio
    async def test_burger_and_fries_order(self):
        """Test ordering a burger and fries in a specific room."""
        # Simulate processing delay
        await asyncio.sleep(5)

        message = "I am in room 102. I would like to order a burger and fries"
        history = []

        # Process the message
        result = await self.agent.process(message, history)

        # Additional processing delay
        await asyncio.sleep(3)

        # Assertions
        assert result is not None
        assert isinstance(result, AgentOutput)
        
        # Check response
        assert "burger and fries" in result.response.lower()
        
        # Check notifications
        assert len(result.notifications) > 0
        notification = result.notifications[0]
        assert notification.get('type') == 'order_started'
        assert notification.get('room_number') == '102'
        assert notification.get('agent') == 'room_service_agent'

    @pytest.mark.asyncio
    async def test_menu_request(self):
        """Test requesting the room service menu."""
        # Simulate processing delay
        await asyncio.sleep(5)

        message = "Can I see the menu?"
        history = []

        # Process the message
        result = await self.agent.process(message, history)

        # Additional processing delay
        await asyncio.sleep(3)

        # Assertions
        assert result is not None
        assert isinstance(result, AgentOutput)
        
        # Check response contains menu details
        assert "BREAKFAST" in result.response
        assert "ALL DAY DINING" in result.response

        # Check notifications
        assert len(result.notifications) > 0
        notification = result.notifications[0]
        assert notification.get('type') == 'menu_viewed'
        assert notification.get('agent') == 'room_service_agent'

    @pytest.mark.asyncio
    async def test_towel_request(self):
        """Test requesting towels."""
        # Simulate processing delay
        await asyncio.sleep(5)

        message = "I need some towels in my room"
        history = []

        # Process the message
        result = await self.agent.process(message, history)

        # Additional processing delay
        await asyncio.sleep(3)

        # Assertions
        assert result is not None
        assert isinstance(result, AgentOutput)
        
        # Check response
        assert "fresh towels" in result.response.lower()

        # Check notifications
        assert len(result.notifications) > 0
        notification = result.notifications[0]
        assert notification.get('type') == 'housekeeping_request'
        assert notification.get('request_type') == 'towels'
        assert notification.get('agent') == 'room_service_agent'

    @pytest.mark.asyncio
    async def test_general_inquiry(self):
        """Test a general room service inquiry."""
        # Simulate processing delay
        await asyncio.sleep(5)

        message = "What services can you help me with?"
        history = []

        # Process the message
        result = await self.agent.process(message, history)

        # Additional processing delay
        await asyncio.sleep(3)

        # Assertions
        assert result is not None
        assert isinstance(result, AgentOutput)
        
        # Check response contains service options
        assert "room service orders" in result.response.lower()
        assert "housekeeping items" in result.response.lower()

        # Check notifications
        assert len(result.notifications) > 0
        notification = result.notifications[0]
        assert notification.get('type') == 'general_inquiry'
        assert notification.get('agent') == 'room_service_agent'

    @pytest.mark.asyncio
    async def test_harmful_content(self):
        """Test handling of harmful content."""
        # Simulate processing delay
        await asyncio.sleep(5)

        message = "I want to discuss politics in my room"
        history = []

        # Process the message
        result = await self.agent.process(message, history)

        # Additional processing delay
        await asyncio.sleep(3)

        # Assertions
        assert result is not None
        assert isinstance(result, AgentOutput)
        
        # Check response
        assert "cannot process messages" in result.response.lower()

    def test_should_handle_method(self):
        """Test the should_handle method with various inputs."""
        test_cases = [
            ("I want a burger", True),
            ("Bring me some fries", True),
            ("Need room service", True),
            ("What's the weather?", False),
            ("Towel request", True)
        ]

        for message, expected in test_cases:
            history = []
            result = self.agent.should_handle(message, history)
            assert result == expected, f"Failed for message: {message}"

# Optional: Add tool handling tests
@pytest.mark.asyncio
async def test_tool_handling():
    """Test the tool handling capabilities of the Room Service Agent."""
    # Simulate processing delay
    await asyncio.sleep(5)

    agent = RoomServiceAgent()

    # Test menu availability check
    menu_check_result = await agent.handle_tool_call(
        "check_menu_availability", 
        {"item_ids": ["burger", "fries"]}
    )
    assert "available_items" in menu_check_result
    assert "estimated_wait" in menu_check_result

    # Additional processing delay
    await asyncio.sleep(3)

    # Test order placement
    order_result = await agent.handle_tool_call(
        "place_order", 
        {
            "room_number": "102", 
            "order_items": ["burger", "fries"],
            "special_instructions": "Extra crispy fries"
        }
    )
    assert "order_id" in order_result
    assert order_result["status"] == "confirmed"
    assert order_result["room_number"] == "102"