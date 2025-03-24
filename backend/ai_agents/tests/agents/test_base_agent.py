"""
Tests for the base agent.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

from agents.base_agent import BaseAgent
from rag.rag_module import RAGQuery, RAGResult

class TestBaseAgent:
    """Test cases for the BaseAgent class."""
    
    @pytest.fixture
    def mock_rag_module(self):
        """Fixture to create a mock RAG module."""
        mock = MagicMock()
        mock.process_query = AsyncMock(return_value=RAGResult(
            query="test query",
            context="test context",
            documents=[]
        ))
        return mock
    
    @pytest.fixture
    def base_agent(self, mock_rag_module):
        """Fixture to create a base agent with a mocked RAG module."""
        # Create a concrete subclass of BaseAgent for testing
        class ConcreteAgent(BaseAgent):
            async def process_message(self, message, state):
                return f"Response to: {message}"
        
        agent = ConcreteAgent("TestAgent")
        agent.rag_module = mock_rag_module
        return agent
    
    def test_init(self):
        """Test initialization of the base agent."""
        agent = BaseAgent("TestAgent")
        assert agent.name == "TestAgent"
        assert agent.rag_module is not None
    
    @pytest.mark.asyncio
    async def test_process_message(self, base_agent, mock_rag_module):
        """Test processing a message with RAG enhancement."""
        # Create a message and state
        message = "What are the hotel amenities?"
        state = {"user_id": "123"}
        
        # Mock the _should_use_rag method to return True
        with patch.object(base_agent, '_should_use_rag', return_value=True):
            # Process the message
            response = await base_agent.process_message(message, state)
            
            # Check that the RAG module was called
            mock_rag_module.process_query.assert_called_once_with(
                RAGQuery(query=message, context=state)
            )
            
            # Check that the RAG context was added to the state
            assert state["rag_context"] == "test context"
            
            # Check the response
            assert response == f"Response to: {message}"
    
    @pytest.mark.asyncio
    async def test_process_message_no_rag(self, base_agent, mock_rag_module):
        """Test processing a message without RAG enhancement."""
        # Create a message and state
        message = "Hello"
        state = {"user_id": "123"}
        
        # Mock the _should_use_rag method to return False
        with patch.object(base_agent, '_should_use_rag', return_value=False):
            # Process the message
            response = await base_agent.process_message(message, state)
            
            # Check that the RAG module was not called
            mock_rag_module.process_query.assert_not_called()
            
            # Check that the RAG context was not added to the state
            assert "rag_context" not in state
            
            # Check the response
            assert response == f"Response to: {message}"
    
    def test_should_use_rag(self, base_agent):
        """Test determining if RAG should be used."""
        # Test with a short message
        assert base_agent._should_use_rag("Hi", {}) is False
        
        # Test with a longer message
        assert base_agent._should_use_rag("This is a longer message that should trigger RAG", {}) is True
        
        # Test with a question
        assert base_agent._should_use_rag("What is the check-in time?", {}) is True
    
    def test_format_rag_context(self, base_agent):
        """Test formatting RAG context for inclusion in prompts."""
        # Test with a non-empty context
        context = "This is the RAG context."
        formatted = base_agent._format_rag_context(context)
        assert "Relevant Hotel Information" in formatted
        assert context in formatted
        
        # Test with an empty context
        assert base_agent._format_rag_context("") == ""
        assert base_agent._format_rag_context(None) == ""
    
    def test_extract_entities(self, base_agent):
        """Test extracting entities from a message."""
        # Test with different entity types
        assert base_agent._extract_entities("Tell me about the rooms")["entity_type"] == "room"
        assert base_agent._extract_entities("What dining options are available?")["entity_type"] == "dining"
        assert base_agent._extract_entities("I want to book a spa treatment")["entity_type"] == "spa"
        assert base_agent._extract_entities("What time is check-in?")["entity_type"] == "check_in_out"
        
        # Test with no recognized entities
        assert "entity_type" not in base_agent._extract_entities("Hello")