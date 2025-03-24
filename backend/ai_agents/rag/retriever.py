"""
Retriever for the RAG module.

This module provides functionality to retrieve relevant documents from
the vector store based on a query.
"""

import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from .vector_store import VectorStore, Document
from .embeddings import EmbeddingGenerator
from .processor import TextProcessor

logger = logging.getLogger(__name__)

class RetrievalResult(BaseModel):
    """Result of a retrieval operation."""
    query: str
    documents: List[Document]
    context: str = ""

class Retriever:
    """Retrieve relevant documents for a query."""
    
    def __init__(self, vector_store: VectorStore, embedding_generator: EmbeddingGenerator):
        """Initialize the retriever.
        
        Args:
            vector_store: Vector store for document retrieval
            embedding_generator: Embedding generator for queries
        """
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
        self.processor = TextProcessor()
        logger.info("Retriever initialized")
    
    async def retrieve(self, query: str, k: int = 5) -> RetrievalResult:
        """Retrieve relevant documents for a query.
        
        Args:
            query: Query to retrieve documents for
            k: Number of documents to retrieve
            
        Returns:
            Retrieval result
        """
        # Preprocess the query
        processed_query = self.processor.preprocess_query(query)
        
        # Generate embedding for query
        query_embedding = self.embedding_generator.generate(processed_query)[0]
        
        # Search for similar documents
        documents = self.vector_store.search(query_embedding, k=k)
        
        # Format context
        context = self._format_context(documents)
        
        logger.info(f"Retrieved {len(documents)} documents for query: {query[:50]}...")
        
        return RetrievalResult(
            query=query,
            documents=documents,
            context=context
        )
    
    def _format_context(self, documents: List[Document]) -> str:
        """Format documents into a context string.
        
        Args:
            documents: Documents to format
            
        Returns:
            Formatted context string
        """
        if not documents:
            return ""
        
        context = "Hotel Information:\n\n"
        
        # Group documents by category
        categories = {}
        for doc in documents:
            category = doc.metadata.get("category", "general").capitalize()
            if category not in categories:
                categories[category] = []
            categories[category].append(doc)
        
        # Format by category
        for category, docs in categories.items():
            context += f"--- {category} ---\n"
            for i, doc in enumerate(docs):
                # Add document content
                context += f"{doc.content}\n\n"
        
        return context
    
    def retrieve_sync(self, query: str, k: int = 5) -> RetrievalResult:
        """Synchronous version of retrieve.
        
        This is a convenience method for non-async contexts.
        
        Args:
            query: Query to retrieve documents for
            k: Number of documents to retrieve
            
        Returns:
            Retrieval result
        """
        # Preprocess the query
        processed_query = self.processor.preprocess_query(query)
        
        # Generate embedding for query
        query_embedding = self.embedding_generator.generate(processed_query)[0]
        
        # Search for similar documents
        documents = self.vector_store.search(query_embedding, k=k)
        
        # Format context
        context = self._format_context(documents)
        
        logger.info(f"Retrieved {len(documents)} documents for query: {query[:50]}...")
        
        return RetrievalResult(
            query=query,
            documents=documents,
            context=context
        )