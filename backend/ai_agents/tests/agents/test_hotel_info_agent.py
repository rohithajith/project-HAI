"""
Tests for the hotel information agent.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

from backend.ai_agents.agents.hotel_info_agent import HotelInfoAgent, HotelInfoInput, HotelInfoOutput
from backend.ai_agents.schemas.message import Message
from backend.ai_agents.rag.rag_module import RAGQuery, RAGResult
from backend.ai_agents.rag.vector_store import Document

class TestHotelInfoAgent:
    """Test cases for the HotelInfoAgent class."""
    
    @pytest.fixture
    def mock_rag_module(self):
        """Fixture to create a mock RAG module."""
        mock = MagicMock()
        mock.process_query = AsyncMock(return_value=RAGResult(
            query="What are the room amenities?",
            context="Hotel Information:\n\n--- Rooms ---\nAll rooms feature air conditioning, flat-screen TVs, and free Wi-Fi.\n\n",
            documents=[
                Document(
                    id="doc1",
                    content="All rooms feature air conditioning, flat-screen TVs, and free Wi-Fi.",
                    metadata={"category": "rooms"}
                )
            ]
        ))
        return mock
    
    @pytest.fixture
    def hotel_info_agent(self, mock_rag_module):
        """Fixture to create a hotel information agent with a mocked RAG module."""
        # Patch all the RAG components for the fixture
        with patch('backend.ai_agents.rag.rag_module.EmbeddingGenerator'), \
             patch('backend.ai_agents.rag.rag_module.VectorStore'), \
             patch('backend.ai_agents.rag.rag_module.Retriever'), \
             patch('backend.ai_agents.rag.rag_module.TextProcessor'), \
             patch('backend.ai_agents.rag.rag_module.RAGModule', return_value=mock_rag_module):
            
            agent = HotelInfoAgent()
            agent.rag_module = mock_rag_module
            return agent
    
    @pytest.mark.asyncio
    async def test_process(self, hotel_info_agent, mock_rag_module):
        """Test processing a hotel information request."""
        # Create input data
        input_data = HotelInfoInput(
            guest_name="John Doe",
            booking_id="B12345",
            messages=[
                Message(sender="user", content="Hello"),
                Message(sender="system", content="How can I help you?"),
                Message(sender="user", content="What amenities do the rooms have?")
            ],
            query_type="rooms"
        )
        
        # Process the input
        result = await hotel_info_agent.process(input_data)
        
        # Check that the RAG module was called
        mock_rag_module.process_query.assert_called_once()
        
        # Check the result
        assert isinstance(result, HotelInfoOutput)
        assert "amenities" in result.response.lower() or "rooms" in result.response.lower()
        assert len(result.suggested_actions) > 0
    
    @pytest.mark.asyncio
    async def test_process_no_messages(self, hotel_info_agent):
        """Test processing a request with no messages."""
        # Create input data with no messages
        input_data = HotelInfoInput(
            guest_name="John Doe",
            booking_id="B12345",
            messages=[],
            query_type="rooms"
        )
        
        # Process the input
        result = await hotel_info_agent.process(input_data)
        
        # Check the result
        assert isinstance(result, HotelInfoOutput)
        assert result.response != ""
        assert len(result.suggested_actions) > 0
    
    def test_generate_response(self, hotel_info_agent):
        """Test generating a response based on context."""
        # Create context
        context = {
            "guest_name": "John Doe",
            "booking_id": "B12345",
            "query_type": "rooms",
            "latest_message": "What amenities do the rooms have?",
            "hotel_info": "All rooms feature air conditioning, flat-screen TVs, and free Wi-Fi."
        }
        
        # Generate response
        response = hotel_info_agent._generate_response(context)
        
        # Check the response
        assert "air conditioning" in response or "TVs" in response or "Wi-Fi" in response
    
    def test_generate_response_no_info(self, hotel_info_agent):
        """Test generating a response with no hotel information."""
        # Create context with no hotel information
        context = {
            "guest_name": "John Doe",
            "booking_id": "B12345",
            "query_type": "rooms",
            "latest_message": "What amenities do the rooms have?",
            "hotel_info": ""
        }
        
        # Generate response
        response = hotel_info_agent._generate_response(context)
        
        # Check the response
        assert "don't have specific information" in response.lower() or "contact the front desk" in response.lower()
    
    def test_generate_suggested_actions(self, hotel_info_agent):
        """Test generating suggested actions based on query type."""
        # Test for different query types
        room_actions = hotel_info_agent._generate_suggested_actions("room")
        dining_actions = hotel_info_agent._generate_suggested_actions("dining")
        spa_actions = hotel_info_agent._generate_suggested_actions("spa")
        check_in_out_actions = hotel_info_agent._generate_suggested_actions("check_in_out")
        general_actions = hotel_info_agent._generate_suggested_actions("general")
        
        # Check that we got different actions for each query type
        assert len(room_actions) > 0
        assert len(dining_actions) > 0
        assert len(spa_actions) > 0
        assert len(check_in_out_actions) > 0
        assert len(general_actions) > 0
        
        # Check that the actions are different
        assert set(room_actions) != set(dining_actions)
        assert set(room_actions) != set(spa_actions)
        assert set(dining_actions) != set(spa_actions)
    
    def test_generate_related_info(self, hotel_info_agent):
        """Test generating related information based on query type and documents."""
        # Create test documents
        documents = [
            Document(
                id="doc1",
                content="All rooms feature air conditioning, flat-screen TVs, and free Wi-Fi.",
                metadata={"category": "rooms"}
            ),
            Document(
                id="doc2",
                content="The restaurant serves breakfast from 7 AM to 10 AM.",
                metadata={"category": "dining"}
            )
        ]
        
        # Generate related information
        related_info = hotel_info_agent._generate_related_info("rooms", documents)
        
        # Check the related information
        assert related_info["category"] == "rooms"
        assert len(related_info["highlights"]) > 0
        assert related_info["highlights"][0]["category"] == "rooms"