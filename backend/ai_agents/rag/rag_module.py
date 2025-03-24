"""
RAG module for the Hotel AI Assistant.

This module provides the main RAG functionality, integrating the vector store,
embedding generator, and retriever components.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from .vector_store import VectorStore, Document
from .embeddings import EmbeddingGenerator
from .retriever import Retriever, RetrievalResult
from .processor import TextProcessor

logger = logging.getLogger(__name__)

class RAGQuery(BaseModel):
    """Query for the RAG module."""
    query: str
    context: Dict[str, Any] = {}

class RAGResult(BaseModel):
    """Result from the RAG module."""
    query: str
    context: str
    documents: List[Document] = []

class RAGModule:
    """RAG module for enhancing LLM responses with hotel information."""
    
    def __init__(self, embedding_dim: int = 768):
        """Initialize the RAG module.
        
        Args:
            embedding_dim: Dimension of embeddings
        """
        # Initialize components
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStore(embedding_dim=embedding_dim)
        self.retriever = Retriever(self.vector_store, self.embedding_generator)
        self.processor = TextProcessor()
        
        logger.info("RAG module initialized")
    
    async def process_query(self, query: RAGQuery) -> RAGResult:
        """Process a query with RAG.
        
        Args:
            query: Query to process
            
        Returns:
            RAG result with enhanced context
        """
        # Retrieve relevant documents
        retrieval_result = await self.retriever.retrieve(query.query)
        
        # Create result
        result = RAGResult(
            query=query.query,
            context=retrieval_result.context,
            documents=retrieval_result.documents
        )
        
        logger.info(f"Processed query with RAG: {query.query[:50]}...")
        
        return result
    
    def ingest_hotel_information(self, text: str, source: str = "hotel_info") -> int:
        """Ingest hotel information into the vector store.
        
        Args:
            text: Hotel information text
            source: Source of the information
            
        Returns:
            Number of chunks ingested
        """
        # Clean text
        cleaned_text = self.processor.clean_text(text)
        
        # Split into chunks
        chunks = self.processor.chunk_text(cleaned_text)
        
        # Create documents
        documents = []
        for i, chunk in enumerate(chunks):
            # Extract metadata
            metadata = self.processor.extract_metadata(chunk)
            metadata["source"] = source
            metadata["chunk_id"] = i
            
            # Create document
            doc = Document(
                id=f"{source}_{i}",
                content=chunk,
                metadata=metadata
            )
            documents.append(doc)
        
        # Generate embeddings
        embeddings = self.embedding_generator.generate([doc.content for doc in documents])
        
        # Add embeddings to documents
        for i, embedding in enumerate(embeddings):
            documents[i].embedding = embedding
        
        # Add to vector store
        self.vector_store.add_documents(documents)
        
        logger.info(f"Ingested {len(documents)} chunks of hotel information")
        
        return len(documents)
    
    def get_hotel_information_by_category(self, category: str, limit: int = 5) -> List[Document]:
        """Get hotel information by category.
        
        Args:
            category: Category to filter by
            limit: Maximum number of documents to return
            
        Returns:
            List of documents in the category
        """
        # This is a placeholder implementation
        # In a real implementation, we would query the vector store by metadata
        # For now, we'll just return an empty list
        return []
    
    def clear_hotel_information(self):
        """Clear all hotel information from the vector store."""
        self.vector_store.clear()
        logger.info("Cleared all hotel information from vector store")