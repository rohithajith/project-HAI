"""
Enhanced RAG module for the Hotel AI Assistant.

This module provides advanced RAG functionality, integrating the vector store,
embedding generator, and retriever components with improved LLM integration,
conversation context handling, and evaluation metrics.
"""

import os
import logging
import json
import asyncio
import time
from typing import List, Dict, Any, Optional, Union, Tuple
from pydantic import BaseModel, Field
from datetime import datetime

from .vector_store import VectorStore, Document
from .embeddings import EmbeddingGenerator
from .retriever import Retriever, RetrievalResult, SearchOptions
from .processor import TextProcessor

logger = logging.getLogger(__name__)

class RAGQuery(BaseModel):
    """Query for the RAG module."""
    query: str
    context: Dict[str, Any] = {}
    search_options: Optional[SearchOptions] = None

class RAGResult(BaseModel):
    """Result from the RAG module."""
    query: str
    context: str
    documents: List[Document] = []
    llm_prompt: Optional[str] = None
    metadata: Dict[str, Any] = {}
    conversation_id: Optional[str] = None

class RAGFeedback(BaseModel):
    """Feedback for a RAG result."""
    query_id: str
    relevant: bool = True
    helpful: bool = True
    missing_info: Optional[str] = None
    comments: Optional[str] = None

class RAGConversation(BaseModel):
    """Conversation history for RAG."""
    id: str
    queries: List[str] = []
    contexts: List[str] = []
    timestamps: List[str] = []

class RAGModule:
    """Enhanced RAG module for LLM responses with advanced features."""
    
    def __init__(self,
                 embedding_dim: int = 768,
                 embedding_model: str = "BAAI/bge-small-en-v1.5",
                 vector_store_type: str = "flat",
                 use_conversation_context: bool = True,
                 cache_dir: Optional[str] = None):
        """Initialize the RAG module with configurable components.
        
        Args:
            embedding_dim: Dimension of embeddings
            embedding_model: Name of the embedding model
            vector_store_type: Type of vector store index
            use_conversation_context: Whether to use conversation context
            cache_dir: Directory for caching
        """
        # Initialize components with enhanced options
        self.embedding_generator = EmbeddingGenerator(
            model_name=embedding_model,
            cache_dir=cache_dir,
            use_cache=True
        )
        
        self.vector_store = VectorStore(
            embedding_dim=embedding_dim,
            index_type=vector_store_type
        )
        
        self.retriever = Retriever(self.vector_store, self.embedding_generator)
        self.processor = TextProcessor()
        
        # Configuration
        self.use_conversation_context = use_conversation_context
        self.cache_dir = cache_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data/rag_cache"
        )
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Conversation tracking
        self.conversations = {}
        self.conversation_file = os.path.join(self.cache_dir, "conversations.json")
        self._load_conversations()
        
        # Feedback tracking
        self.feedback = {}
        self.feedback_file = os.path.join(self.cache_dir, "feedback.json")
        self._load_feedback()
        
        # Performance metrics
        self.metrics = {
            "queries_processed": 0,
            "avg_retrieval_time": 0,
            "total_retrieval_time": 0,
            "cache_hits": 0,
            "feedback_count": 0
        }
        
        logger.info(f"Enhanced RAG module initialized with {embedding_model} embeddings")
    
    async def process_query(self, query: RAGQuery) -> RAGResult:
        """Process a query with enhanced RAG capabilities.
        
        Args:
            query: Query to process
            
        Returns:
            RAG result with enhanced context
        """
        start_time = time.time()
        
        # Get conversation ID from context or generate a new one
        conversation_id = query.context.get("conversation_id")
        if not conversation_id and self.use_conversation_context:
            conversation_id = f"conv_{int(time.time())}"
            query.context["conversation_id"] = conversation_id
        
        # Get conversation history if available
        conversation_context = ""
        if self.use_conversation_context and conversation_id:
            conversation = self.conversations.get(conversation_id)
            if conversation:
                # Use recent conversation history
                recent_queries = conversation.queries[-3:] if len(conversation.queries) > 0 else []
                recent_contexts = conversation.contexts[-3:] if len(conversation.contexts) > 0 else []
                
                # Add conversation context to query
                if recent_queries and recent_contexts:
                    conversation_context = "\n\nConversation History:\n"
                    for q, c in zip(recent_queries, recent_contexts):
                        conversation_context += f"User: {q}\nContext: {c}\n\n"
        
        # Create search options from query context
        search_options = query.search_options or SearchOptions()
        
        # Extract query type from context
        query_type = query.context.get("query_type")
        if query_type and not search_options.filter_categories:
            # Map query type to categories
            category_mapping = {
                "room": ["rooms", "amenities"],
                "dining": ["dining", "restaurant"],
                "spa": ["spa", "wellness"],
                "check_in_out": ["policies", "check-in"],
                "facilities": ["facilities", "amenities"],
                "general": []
            }
            search_options.filter_categories = category_mapping.get(query_type, [])
        
        # Retrieve relevant documents
        retrieval_result = await self.retriever.retrieve(query.query, search_options)
        
        # Generate LLM prompt
        llm_prompt = self._generate_llm_prompt(
            query.query,
            retrieval_result.context,
            conversation_context,
            query.context
        )
        
        # Create result
        result = RAGResult(
            query=query.query,
            context=retrieval_result.context,
            documents=retrieval_result.documents,
            llm_prompt=llm_prompt,
            conversation_id=conversation_id,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "retrieval_time": time.time() - start_time,
                "document_count": len(retrieval_result.documents),
                "categories": list(set(doc.metadata.get("category", "general") for doc in retrieval_result.documents)),
                "expanded_queries": retrieval_result.expanded_queries,
                "search_type": retrieval_result.search_type
            }
        )
        
        # Update conversation history
        if self.use_conversation_context and conversation_id:
            self._update_conversation(conversation_id, query.query, retrieval_result.context)
        
        # Update metrics
        self.metrics["queries_processed"] += 1
        self.metrics["total_retrieval_time"] += (time.time() - start_time)
        self.metrics["avg_retrieval_time"] = self.metrics["total_retrieval_time"] / self.metrics["queries_processed"]
        
        logger.info(f"Processed query with enhanced RAG: {query.query[:50]}... in {time.time() - start_time:.2f}s")
        
        return result
    
    def _generate_llm_prompt(self, query: str, context: str, conversation_context: str,
                            user_context: Dict[str, Any]) -> str:
        """Generate a prompt for the LLM based on the RAG context.
        
        Args:
            query: User query
            context: RAG context
            conversation_context: Conversation history
            user_context: User context information
            
        Returns:
            Formatted prompt for the LLM
        """
        # Extract user information
        guest_name = user_context.get("guest_name", "Guest")
        booking_id = user_context.get("booking_id", "")
        
        # Build prompt
        prompt = f"""You are a helpful hotel assistant providing information to {guest_name}.

User Query: {query}

{context}

{conversation_context}

Additional Information:
- Guest Name: {guest_name}
- Booking ID: {booking_id if booking_id else "Not provided"}
- Current Time: {datetime.now().strftime("%A, %B %d, %Y %I:%M %p")}

Instructions:
1. Answer the user's query based on the hotel information provided above.
2. If the information is not in the context, politely state that you don't have that specific information.
3. Be concise, helpful, and friendly in your response.
4. Do not make up information that is not in the provided context.
5. If the user asks about booking or making reservations, direct them to the appropriate channels.

Your response:
"""
        return prompt
    
    def _update_conversation(self, conversation_id: str, query: str, context: str):
        """Update conversation history.
        
        Args:
            conversation_id: Conversation ID
            query: User query
            context: RAG context
        """
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = RAGConversation(
                id=conversation_id,
                queries=[],
                contexts=[],
                timestamps=[]
            )
        
        # Add to conversation history
        conversation = self.conversations[conversation_id]
        conversation.queries.append(query)
        conversation.contexts.append(context[:500] + "..." if len(context) > 500 else context)  # Truncate for storage
        conversation.timestamps.append(datetime.now().isoformat())
        
        # Limit history size
        if len(conversation.queries) > 10:
            conversation.queries = conversation.queries[-10:]
            conversation.contexts = conversation.contexts[-10:]
            conversation.timestamps = conversation.timestamps[-10:]
        
        # Save conversations periodically
        if len(self.conversations) % 10 == 0:
            self._save_conversations()
    
    def _load_conversations(self):
        """Load conversation history from disk."""
        if os.path.exists(self.conversation_file):
            try:
                with open(self.conversation_file, 'r') as f:
                    conversations_data = json.load(f)
                
                for conv_id, conv_data in conversations_data.items():
                    self.conversations[conv_id] = RAGConversation(**conv_data)
                
                logger.info(f"Loaded {len(self.conversations)} conversations from disk")
            except Exception as e:
                logger.warning(f"Failed to load conversations: {e}")
    
    def _save_conversations(self):
        """Save conversation history to disk."""
        try:
            # Convert to dictionary
            conversations_data = {
                conv_id: conv.dict() for conv_id, conv in self.conversations.items()
            }
            
            with open(self.conversation_file, 'w') as f:
                json.dump(conversations_data, f, indent=2)
            
            logger.info(f"Saved {len(self.conversations)} conversations to disk")
        except Exception as e:
            logger.warning(f"Failed to save conversations: {e}")
    
    def _load_feedback(self):
        """Load feedback from disk."""
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r') as f:
                    self.feedback = json.load(f)
                
                logger.info(f"Loaded {len(self.feedback)} feedback entries from disk")
            except Exception as e:
                logger.warning(f"Failed to load feedback: {e}")
    
    def _save_feedback(self):
        """Save feedback to disk."""
        try:
            with open(self.feedback_file, 'w') as f:
                json.dump(self.feedback, f, indent=2)
            
            logger.info(f"Saved {len(self.feedback)} feedback entries to disk")
        except Exception as e:
            logger.warning(f"Failed to save feedback: {e}")
    
    async def ingest_hotel_information(self, text: str, source: str = "hotel_info",
                                      chunk_method: str = "paragraph") -> int:
        """Ingest hotel information with advanced chunking options.
        
        Args:
            text: Hotel information text
            source: Source of the information
            chunk_method: Method for chunking text ("word", "sentence", "paragraph")
            
        Returns:
            Number of chunks ingested
        """
        # Clean text
        cleaned_text = self.processor.clean_text(text)
        
        # Split into chunks with specified method
        chunks = self.processor.chunk_text(
            cleaned_text,
            chunk_by=chunk_method,
            respect_paragraphs=True
        )
        
        # Create documents
        documents = []
        for i, chunk in enumerate(chunks):
            # Extract rich metadata
            metadata = self.processor.extract_metadata(chunk)
            metadata["source"] = source
            metadata["chunk_id"] = i
            metadata["ingestion_time"] = datetime.now().isoformat()
            
            # Create document
            doc = Document(
                id=f"{source}_{int(time.time())}_{i}",
                content=chunk,
                metadata=metadata
            )
            documents.append(doc)
        
        # Generate embeddings asynchronously
        embeddings = await self.embedding_generator.generate_async([doc.content for doc in documents])
        
        # Add embeddings to documents
        for i, embedding in enumerate(embeddings):
            documents[i].embedding = embedding
        
        # Add to vector store
        self.vector_store.add_documents(documents)
        
        logger.info(f"Ingested {len(documents)} chunks of hotel information from {source}")
        
        return len(documents)
    
    def get_hotel_information_by_category(self, category: str, limit: int = 5) -> List[Document]:
        """Get hotel information by category.
        
        Args:
            category: Category to filter by
            limit: Maximum number of documents to return
            
        Returns:
            List of documents in the category
        """
        # Use vector store's metadata filtering
        return self.vector_store.get_documents_by_metadata({"category": category}, limit=limit)
    
    def add_feedback(self, feedback: RAGFeedback):
        """Add feedback for a RAG result.
        
        Args:
            feedback: Feedback data
        """
        # Add feedback
        self.feedback[feedback.query_id] = feedback.dict()
        
        # Update metrics
        self.metrics["feedback_count"] += 1
        
        # Save feedback
        self._save_feedback()
        
        logger.info(f"Added feedback for query {feedback.query_id}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get RAG module metrics.
        
        Returns:
            Dictionary of metrics
        """
        # Add component metrics
        metrics = {
            **self.metrics,
            "vector_store": self.vector_store.get_stats().dict(),
            "embedding_model": self.embedding_generator.get_model_info(),
            "conversation_count": len(self.conversations),
            "feedback_count": len(self.feedback)
        }
        
        return metrics
    
    def clear_hotel_information(self):
        """Clear all hotel information from the vector store."""
        self.vector_store.clear()
        logger.info("Cleared all hotel information from vector store")
    
    def clear_caches(self):
        """Clear all caches."""
        self.retriever.clear_cache()
        logger.info("Cleared retriever cache")