"""
Retriever for the RAG module.

This module provides advanced functionality to retrieve relevant documents from
the vector store based on a query, with support for hybrid search, reranking,
and query expansion.
"""

import logging
import re
import asyncio
from typing import List, Dict, Any, Optional, Tuple, Union, Set
from pydantic import BaseModel, Field
import json
from datetime import datetime

from .vector_store import VectorStore, Document
from .embeddings import EmbeddingGenerator
from .processor import TextProcessor

logger = logging.getLogger(__name__)

class RetrievalResult(BaseModel):
    """Result of a retrieval operation."""
    query: str
    documents: List[Document]
    context: str = ""
    expanded_queries: List[str] = []
    search_type: str = "semantic"
    metadata: Dict[str, Any] = {}

class SearchOptions(BaseModel):
    """Options for search operations."""
    k: int = 5
    search_type: str = "hybrid"  # "semantic", "keyword", "hybrid"
    expand_query: bool = True
    filter_categories: List[str] = []
    min_score: float = 0.0
    rerank: bool = True
    include_metadata: bool = True
    context_format: str = "category"  # "category", "relevance", "raw"

class Retriever:
    """Advanced retriever for relevant documents."""
    
    def __init__(self, vector_store: VectorStore, embedding_generator: EmbeddingGenerator):
        """Initialize the retriever.
        
        Args:
            vector_store: Vector store for document retrieval
            embedding_generator: Embedding generator for queries
        """
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
        self.processor = TextProcessor()
        
        # Initialize cache
        self.query_cache = {}
        self.cache_size = 100
        
        logger.info("Advanced retriever initialized")
    
    async def retrieve(self, query: str, options: Optional[SearchOptions] = None) -> RetrievalResult:
        """Retrieve relevant documents for a query with advanced options.
        
        Args:
            query: Query to retrieve documents for
            options: Search options
            
        Returns:
            Retrieval result
        """
        # Use default options if none provided
        if options is None:
            options = SearchOptions()
        
        # Check cache first
        cache_key = self._get_cache_key(query, options)
        if cache_key in self.query_cache:
            logger.info(f"Retrieved result from cache for query: {query[:50]}...")
            return self.query_cache[cache_key]
        
        # Start timing
        start_time = datetime.now()
        
        # Preprocess the query
        processed_query = self.processor.preprocess_query(query)
        
        # Expand query if requested
        expanded_queries = [processed_query]
        if options.expand_query:
            expanded_queries = self.processor.generate_query_variations(processed_query)
            logger.info(f"Expanded query to {len(expanded_queries)} variations")
        
        # Perform search based on search type
        if options.search_type == "semantic":
            documents = await self._semantic_search(expanded_queries, options.k)
        elif options.search_type == "keyword":
            documents = self._keyword_search(expanded_queries, options.k)
        else:  # hybrid
            semantic_docs = await self._semantic_search(expanded_queries, options.k * 2)
            keyword_docs = self._keyword_search(expanded_queries, options.k * 2)
            documents = self._merge_results(semantic_docs, keyword_docs, options.k)
        
        # Apply filters
        if options.filter_categories:
            documents = [doc for doc in documents if
                        doc.metadata.get("category") in options.filter_categories]
        
        # Apply minimum score filter
        if options.min_score > 0:
            documents = [doc for doc in documents if
                        doc.metadata.get("score", 1.0) >= options.min_score]
        
        # Rerank results if requested
        if options.rerank and len(documents) > 1:
            documents = self._rerank_results(documents, processed_query)
        
        # Format context
        context = self._format_context(documents, format_type=options.context_format)
        
        # Calculate timing
        elapsed_time = (datetime.now() - start_time).total_seconds()
        
        # Create result
        result = RetrievalResult(
            query=query,
            documents=documents,
            context=context,
            expanded_queries=expanded_queries,
            search_type=options.search_type,
            metadata={
                "retrieval_time_seconds": elapsed_time,
                "document_count": len(documents),
                "categories": list(set(doc.metadata.get("category", "general") for doc in documents)),
                "query_variations_count": len(expanded_queries)
            }
        )
        
        # Cache result
        self._add_to_cache(cache_key, result)
        
        logger.info(f"Retrieved {len(documents)} documents for query: {query[:50]}... in {elapsed_time:.2f}s")
        
        return result
    
    async def _semantic_search(self, queries: List[str], k: int) -> List[Document]:
        """Perform semantic search for multiple query variations.
        
        Args:
            queries: List of query variations
            k: Number of documents to retrieve
            
        Returns:
            List of documents
        """
        # Generate embeddings for all queries
        all_embeddings = await self.embedding_generator.generate_async(queries)
        
        # Search for each query embedding
        all_documents = []
        doc_ids = set()  # Track document IDs to avoid duplicates
        
        for query_embedding in all_embeddings:
            # Search vector store
            documents = self.vector_store.search(query_embedding, k=k)
            
            # Add unique documents
            for doc in documents:
                if doc.id not in doc_ids:
                    all_documents.append(doc)
                    doc_ids.add(doc.id)
        
        # Sort by score
        all_documents.sort(key=lambda x: x.metadata.get("score", 1.0))
        
        # Limit to k documents
        return all_documents[:k]
    
    def _keyword_search(self, queries: List[str], k: int) -> List[Document]:
        """Perform keyword search for multiple query variations.
        
        Args:
            queries: List of query variations
            k: Number of documents to retrieve
            
        Returns:
            List of documents
        """
        # Extract keywords from queries
        all_keywords = set()
        for query in queries:
            keywords = self.processor.extract_keywords(query)
            all_keywords.update(keywords)
        
        # Get all documents from vector store
        all_documents = self.vector_store.get_all_documents()
        
        # Score documents based on keyword matches
        scored_docs = []
        for doc in all_documents:
            score = 0
            for keyword in all_keywords:
                # Count occurrences of keyword in document
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, doc.content, re.IGNORECASE)
                score += len(matches)
            
            if score > 0:
                # Create a copy of the document with the score
                doc_copy = Document(
                    id=doc.id,
                    content=doc.content,
                    metadata={**doc.metadata, "score": score},
                    embedding=doc.embedding
                )
                scored_docs.append(doc_copy)
        
        # Sort by score (descending)
        scored_docs.sort(key=lambda x: x.metadata.get("score", 0), reverse=True)
        
        # Limit to k documents
        return scored_docs[:k]
    
    def _merge_results(self, semantic_docs: List[Document], keyword_docs: List[Document], k: int) -> List[Document]:
        """Merge semantic and keyword search results.
        
        Args:
            semantic_docs: Documents from semantic search
            keyword_docs: Documents from keyword search
            k: Number of documents to return
            
        Returns:
            Merged list of documents
        """
        # Create a dictionary of documents by ID
        doc_dict = {}
        
        # Add semantic documents with normalized scores
        max_semantic_score = max([doc.metadata.get("score", 1.0) for doc in semantic_docs]) if semantic_docs else 1.0
        for doc in semantic_docs:
            normalized_score = doc.metadata.get("score", 1.0) / max_semantic_score
            doc_dict[doc.id] = Document(
                id=doc.id,
                content=doc.content,
                metadata={**doc.metadata, "score": normalized_score, "source": "semantic"},
                embedding=doc.embedding
            )
        
        # Add keyword documents with normalized scores
        max_keyword_score = max([doc.metadata.get("score", 1.0) for doc in keyword_docs]) if keyword_docs else 1.0
        for doc in keyword_docs:
            normalized_score = doc.metadata.get("score", 1.0) / max_keyword_score if max_keyword_score > 0 else 0
            
            if doc.id in doc_dict:
                # Document already exists from semantic search, combine scores
                existing_doc = doc_dict[doc.id]
                combined_score = (existing_doc.metadata.get("score", 0) + normalized_score) / 2
                doc_dict[doc.id] = Document(
                    id=doc.id,
                    content=doc.content,
                    metadata={**doc.metadata, "score": combined_score, "source": "hybrid"},
                    embedding=doc.embedding
                )
            else:
                # New document from keyword search
                doc_dict[doc.id] = Document(
                    id=doc.id,
                    content=doc.content,
                    metadata={**doc.metadata, "score": normalized_score, "source": "keyword"},
                    embedding=doc.embedding
                )
        
        # Convert dictionary to list and sort by score
        merged_docs = list(doc_dict.values())
        merged_docs.sort(key=lambda x: x.metadata.get("score", 0), reverse=True)
        
        # Limit to k documents
        return merged_docs[:k]
    
    def _rerank_results(self, documents: List[Document], query: str) -> List[Document]:
        """Rerank results based on additional criteria.
        
        Args:
            documents: Documents to rerank
            query: Original query
            
        Returns:
            Reranked documents
        """
        # Extract query keywords
        query_keywords = set(self.processor.extract_keywords(query))
        
        # Score documents based on multiple factors
        for i, doc in enumerate(documents):
            base_score = doc.metadata.get("score", 1.0)
            
            # Factor 1: Keyword density
            keyword_matches = 0
            for keyword in query_keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, doc.content, re.IGNORECASE)
                keyword_matches += len(matches)
            
            keyword_density = keyword_matches / max(1, len(doc.content.split()))
            
            # Factor 2: Category relevance
            category_boost = 0.0
            doc_category = doc.metadata.get("category", "general")
            
            # Check if query contains category keywords
            for category, keywords in self.processor.HOTEL_CATEGORIES.items():
                if any(keyword in query.lower() for keyword in keywords):
                    if category == doc_category:
                        category_boost = 0.2
                        break
            
            # Factor 3: Sentiment alignment
            sentiment_boost = 0.0
            if "sentiment" in doc.metadata:
                # If query has positive words, boost positive documents
                if re.search(r'\b(good|great|best|excellent|recommend)\b', query, re.IGNORECASE):
                    if doc.metadata["sentiment"] == "positive":
                        sentiment_boost = 0.1
                
                # If query has negative words, boost negative documents
                if re.search(r'\b(bad|worst|avoid|problem|issue)\b', query, re.IGNORECASE):
                    if doc.metadata["sentiment"] == "negative":
                        sentiment_boost = 0.1
            
            # Combine factors
            final_score = base_score * (1.0 + keyword_density + category_boost + sentiment_boost)
            
            # Update document score
            documents[i] = Document(
                id=doc.id,
                content=doc.content,
                metadata={**doc.metadata, "score": final_score, "reranked": True},
                embedding=doc.embedding
            )
        
        # Sort by final score
        documents.sort(key=lambda x: x.metadata.get("score", 0), reverse=True)
        
        return documents
    
    def _format_context(self, documents: List[Document], format_type: str = "category") -> str:
        """Format documents into a context string with different formatting options.
        
        Args:
            documents: Documents to format
            format_type: Type of formatting to use
            
        Returns:
            Formatted context string
        """
        if not documents:
            return ""
        
        if format_type == "category":
            # Group by category
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
        
        elif format_type == "relevance":
            # Sort by relevance score
            context = "Hotel Information (most relevant first):\n\n"
            
            # Sort documents by score
            sorted_docs = sorted(documents, key=lambda x: x.metadata.get("score", 0), reverse=True)
            
            # Format by relevance
            for i, doc in enumerate(sorted_docs):
                category = doc.metadata.get("category", "general").capitalize()
                score = doc.metadata.get("score", 0)
                
                context += f"[{category}] {doc.content}\n\n"
        
        else:  # raw
            # Simple concatenation
            context = "\n\n".join([doc.content for doc in documents])
        
        return context
    
    def _get_cache_key(self, query: str, options: SearchOptions) -> str:
        """Generate a cache key for a query and options.
        
        Args:
            query: Query string
            options: Search options
            
        Returns:
            Cache key
        """
        # Create a dictionary of the query and options
        cache_dict = {
            "query": query,
            "k": options.k,
            "search_type": options.search_type,
            "expand_query": options.expand_query,
            "filter_categories": sorted(options.filter_categories) if options.filter_categories else [],
            "min_score": options.min_score,
            "rerank": options.rerank,
            "context_format": options.context_format
        }
        
        # Convert to JSON string and hash
        return json.dumps(cache_dict)
    
    def _add_to_cache(self, key: str, result: RetrievalResult) -> None:
        """Add a result to the cache.
        
        Args:
            key: Cache key
            result: Retrieval result
        """
        # Add to cache
        self.query_cache[key] = result
        
        # Limit cache size
        if len(self.query_cache) > self.cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.query_cache))
            del self.query_cache[oldest_key]
    
    def retrieve_sync(self, query: str, options: Optional[SearchOptions] = None) -> RetrievalResult:
        """Synchronous version of retrieve.
        
        Args:
            query: Query to retrieve documents for
            options: Search options
            
        Returns:
            Retrieval result
        """
        # Create event loop
        loop = asyncio.new_event_loop()
        try:
            # Run retrieve asynchronously
            return loop.run_until_complete(self.retrieve(query, options))
        finally:
            # Close event loop
            loop.close()
    
    def clear_cache(self) -> None:
        """Clear the query cache."""
        self.query_cache = {}
        logger.info("Cleared retriever cache")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retriever statistics.
        
        Returns:
            Dictionary of statistics
        """
        return {
            "cache_size": len(self.query_cache),
            "cache_limit": self.cache_size,
            "vector_store_size": self.vector_store.get_document_count(),
            "embedding_model": self.embedding_generator.get_model_info()
        }