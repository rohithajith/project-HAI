"""
Tests for the main RAG module.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

from rag.rag_module import RAGModule, RAGQuery, RAGResult
from rag.vector_store import Document

class TestRAGModule:
    """Test cases for the RAGModule class."""
    
    @pytest.fixture
    def mock_embedding_generator(self):
        """Fixture to create a mock embedding generator."""
        mock = MagicMock()
        mock.generate.return_value = [[0.1] * 768]
        return mock
    
    @pytest.fixture
    def mock_vector_store(self):
        """Fixture to create a mock vector store."""
        mock = MagicMock()
        mock.add_documents.return_value = None
        return mock
    
    @pytest.fixture
    def mock_retriever(self):
        """Fixture to create a mock retriever."""
        mock = MagicMock()
        mock.retrieve = AsyncMock(return_value=MagicMock(
            query="test query",
            documents=[
                Document(
                    id="doc1",
                    content="This is document 1",
                    metadata={"category": "rooms"}
                )
            ],
            context="Hotel Information:\n\n--- Rooms ---\nThis is document 1\n\n"
        ))
        return mock
    
    @pytest.fixture
    def mock_processor(self):
        """Fixture to create a mock text processor."""
        mock = MagicMock()
        mock.clean_text.return_value = "cleaned text"
        mock.chunk_text.return_value = ["chunk1", "chunk2"]
        mock.extract_metadata.return_value = {"category": "rooms"}
        return mock
    
    @pytest.fixture
    def rag_module(self, mock_embedding_generator, mock_vector_store, mock_retriever, mock_processor):
        """Fixture to create a RAG module with mocked dependencies."""
        with patch('rag.rag_module.EmbeddingGenerator', return_value=mock_embedding_generator), \
             patch('rag.rag_module.VectorStore', return_value=mock_vector_store), \
             patch('rag.rag_module.Retriever', return_value=mock_retriever), \
             patch('rag.rag_module.TextProcessor', return_value=mock_processor):
            module = RAGModule()
            # Replace the processor with our mock
            module.processor = mock_processor
            return module
    
    @pytest.mark.asyncio
    async def test_process_query(self, rag_module, mock_retriever):
        """Test processing a query."""
        # Create a query
        query = RAGQuery(query="What are the room amenities?", context={"user_id": "123"})
        
        # Process the query
        result = await rag_module.process_query(query)
        
        # Check that the retriever was called
        mock_retriever.retrieve.assert_called_once_with("What are the room amenities?")
        
        # Check the result
        assert isinstance(result, RAGResult)
        assert result.query == "What are the room amenities?"
        assert len(result.documents) == 1
        assert result.context == "Hotel Information:\n\n--- Rooms ---\nThis is document 1\n\n"
    
    def test_ingest_hotel_information(self, rag_module, mock_processor, mock_embedding_generator, mock_vector_store):
        """Test ingesting hotel information."""
        # Ingest hotel information
        chunks = rag_module.ingest_hotel_information("This is hotel information", source="test")
        
        # Check that the text was processed
        mock_processor.clean_text.assert_called_once_with("This is hotel information")
        mock_processor.chunk_text.assert_called_once_with("cleaned text")
        
        # Check that metadata was extracted
        assert mock_processor.extract_metadata.call_count == 2
        
        # Check that embeddings were generated
        mock_embedding_generator.generate.assert_called_once_with(["chunk1", "chunk2"])
        
        # Check that documents were added to the vector store
        mock_vector_store.add_documents.assert_called_once()
        
        # Check the return value
        assert chunks == 2
    
    def test_ingest_hotel_information_empty(self, rag_module, mock_processor):
        """Test ingesting empty hotel information."""
        # Mock chunk_text to return an empty list
        mock_processor.chunk_text.return_value = []
        
        # Ingest hotel information
        chunks = rag_module.ingest_hotel_information("", source="test")
        
        # Check the return value
        assert chunks == 0
    
    def test_clear_hotel_information(self, rag_module, mock_vector_store):
        """Test clearing hotel information."""
        # Clear hotel information
        rag_module.clear_hotel_information()
        
        # Check that the vector store was cleared
        mock_vector_store.clear.assert_called_once()