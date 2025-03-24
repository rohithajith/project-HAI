"""
Tests for the retriever module.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

from rag.retriever import Retriever, RetrievalResult
from rag.vector_store import Document

class TestRetriever:
    """Test cases for the Retriever class."""
    
    @pytest.fixture
    def mock_vector_store(self):
        """Fixture to create a mock vector store."""
        mock = MagicMock()
        mock.search.return_value = [
            Document(
                id="doc1",
                content="This is document 1",
                metadata={"category": "rooms", "score": 0.8}
            ),
            Document(
                id="doc2",
                content="This is document 2",
                metadata={"category": "dining", "score": 0.6}
            )
        ]
        return mock
    
    @pytest.fixture
    def mock_embedding_generator(self):
        """Fixture to create a mock embedding generator."""
        mock = MagicMock()
        mock.generate.return_value = [[0.1] * 768]
        return mock
    
    @pytest.fixture
    def retriever(self, mock_vector_store, mock_embedding_generator):
        """Fixture to create a retriever with mocked dependencies."""
        return Retriever(mock_vector_store, mock_embedding_generator)
    
    @pytest.mark.asyncio
    async def test_retrieve(self, retriever, mock_vector_store, mock_embedding_generator):
        """Test retrieving documents."""
        # Mock the preprocess_query method
        with patch.object(retriever.processor, 'preprocess_query', return_value="processed query"):
            # Call the retrieve method
            result = await retriever.retrieve("What are the room amenities?")
            
            # Check that the query was preprocessed
            retriever.processor.preprocess_query.assert_called_once_with("What are the room amenities?")
            
            # Check that the embedding was generated
            mock_embedding_generator.generate.assert_called_once_with("processed query")
            
            # Check that the vector store was searched
            mock_vector_store.search.assert_called_once()
            
            # Check the result
            assert isinstance(result, RetrievalResult)
            assert result.query == "What are the room amenities?"
            assert len(result.documents) == 2
            assert result.context != ""
    
    def test_format_context(self, retriever):
        """Test formatting documents into a context string."""
        # Create test documents
        documents = [
            Document(
                id="doc1",
                content="This is document 1",
                metadata={"category": "rooms"}
            ),
            Document(
                id="doc2",
                content="This is document 2",
                metadata={"category": "dining"}
            )
        ]
        
        # Format the context
        context = retriever._format_context(documents)
        
        # Check the context
        assert "Hotel Information" in context
        assert "Rooms" in context
        assert "Dining" in context
        assert "This is document 1" in context
        assert "This is document 2" in context
    
    def test_format_context_empty(self, retriever):
        """Test formatting an empty list of documents."""
        context = retriever._format_context([])
        assert context == ""
    
    def test_retrieve_sync(self, retriever, mock_vector_store, mock_embedding_generator):
        """Test the synchronous version of retrieve."""
        # Mock the preprocess_query method
        with patch.object(retriever.processor, 'preprocess_query', return_value="processed query"):
            # Call the retrieve_sync method
            result = retriever.retrieve_sync("What are the room amenities?")
            
            # Check that the query was preprocessed
            retriever.processor.preprocess_query.assert_called_once_with("What are the room amenities?")
            
            # Check that the embedding was generated
            mock_embedding_generator.generate.assert_called_once_with("processed query")
            
            # Check that the vector store was searched
            mock_vector_store.search.assert_called_once()
            
            # Check the result
            assert isinstance(result, RetrievalResult)
            assert result.query == "What are the room amenities?"
            assert len(result.documents) == 2
            assert result.context != ""