"""
Hotel Information Agent for the Hotel AI system.

This agent specializes in providing information about the hotel,
leveraging the enhanced RAG module for accurate and contextual responses
with LLM integration.
"""

import logging
import json
import asyncio
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import os

from .base_agent import BaseAgent
from ..schemas.message import Message
from ..schemas.agent_io import AgentInput, AgentOutput
from ..rag.rag_module import RAGQuery, RAGFeedback, SearchOptions
from ..rag.vector_store import Document
from ..rag.retriever import SearchOptions

logger = logging.getLogger(__name__)

class HotelInfoInput(AgentInput):
    """Input for the hotel information agent."""
    guest_name: Optional[str] = None
    booking_id: Optional[str] = None
    messages: List[Message] = []
    query_type: Optional[str] = None  # e.g., "room", "dining", "spa", "general"
    conversation_id: Optional[str] = None
    search_options: Optional[Dict[str, Any]] = None

class HotelInfoOutput(AgentOutput):
    """Output from the hotel information agent."""
    response: str
    suggested_actions: List[str] = []
    related_info: Optional[Dict[str, Any]] = None
    conversation_id: Optional[str] = None
    query_id: Optional[str] = None
    debug_info: Optional[Dict[str, Any]] = None

class HotelInfoAgent(BaseAgent):
    """Enhanced agent for providing hotel information with LLM integration."""
    
    def __init__(self, llm_service=None):
        """Initialize the hotel information agent with optional LLM service.
        
        Args:
            llm_service: Service for LLM integration (optional)
        """
        super().__init__("HotelInfoAgent")
        self.llm_service = llm_service
        
        # Load response templates
        self.templates_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data/templates/hotel_info_templates.json"
        )
        self.response_templates = self._load_templates()
        
        logger.info("Enhanced Hotel Information Agent initialized")
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load response templates from file.
        
        Returns:
            Dictionary of templates
        """
        default_templates = {
            "no_info": "I don't have specific information about {query_type} at the moment. Please contact the front desk for assistance.",
            "general_response": "Here's what I found about {query_type}:\n\n{hotel_info}",
            "greeting": "Hello {guest_name}! How can I help you with information about our hotel today?",
            "error": "I'm sorry, but I encountered an issue while processing your request. Please try again or contact our staff for assistance."
        }
        
        try:
            if os.path.exists(self.templates_path):
                with open(self.templates_path, 'r') as f:
                    return json.load(f)
            else:
                # Create default templates file
                os.makedirs(os.path.dirname(self.templates_path), exist_ok=True)
                with open(self.templates_path, 'w') as f:
                    json.dump(default_templates, f, indent=2)
                return default_templates
        except Exception as e:
            logger.warning(f"Failed to load templates: {e}")
            return default_templates
    
    async def process(self, input_data: HotelInfoInput) -> HotelInfoOutput:
        """Process a hotel information request with enhanced RAG and LLM integration.
        
        Args:
            input_data: The hotel information request data
            
        Returns:
            The hotel information response
        """
        start_time = time.time()
        query_id = f"query_{int(time.time())}"
        logger.info(f"Processing hotel information request: {input_data.query_type} (ID: {query_id})")
        
        try:
            # Extract the latest user message
            latest_message = input_data.messages[-1].content if input_data.messages else ""
            
            # Create search options from input
            search_options = None
            if input_data.search_options:
                search_options = SearchOptions(**input_data.search_options)
            
            # Create state for RAG processing
            state = {
                "booking_id": input_data.booking_id,
                "guest_name": input_data.guest_name,
                "query_type": input_data.query_type,
                "conversation_id": input_data.conversation_id,
                "messages": [{"role": m.sender, "content": m.content} for m in input_data.messages],
                "query_id": query_id,
                "timestamp": datetime.now().isoformat()
            }
            
            # Process with enhanced RAG
            rag_result = await self.rag_module.process_query(
                RAGQuery(
                    query=latest_message,
                    context=state,
                    search_options=search_options
                )
            )
            
            # Extract conversation ID from result
            conversation_id = rag_result.conversation_id or input_data.conversation_id
            
            # Generate response using LLM if available, otherwise use template-based approach
            if self.llm_service and rag_result.llm_prompt:
                response = await self._generate_llm_response(rag_result.llm_prompt)
            else:
                # Extract entities from the message for better context
                entities = self._extract_entities(latest_message)
                
                # Prepare context for response generation
                context = {
                    "guest_name": input_data.guest_name or "Guest",
                    "booking_id": input_data.booking_id,
                    "query_type": input_data.query_type or entities.get("entity_type", "general"),
                    "conversation_history": "\n".join([f"{m.sender}: {m.content}" for m in input_data.messages[:-1]]),
                    "latest_message": latest_message,
                    "hotel_info": rag_result.context,
                    "query_id": query_id,
                    "conversation_id": conversation_id
                }
                
                # Generate response based on context
                response = self._generate_template_response(context)
            
            # Generate suggested actions based on the query type and documents
            query_type = input_data.query_type or self._infer_query_type(latest_message, rag_result.documents)
            suggested_actions = self._generate_suggested_actions(query_type, rag_result.documents)
            
            # Generate related information
            related_info = self._generate_related_info(query_type, rag_result.documents)
            
            # Add debug information if needed
            debug_info = None
            if os.environ.get("RAG_DEBUG", "").lower() == "true":
                debug_info = {
                    "processing_time": time.time() - start_time,
                    "rag_metadata": rag_result.metadata,
                    "document_count": len(rag_result.documents),
                    "categories": list(set(doc.metadata.get("category", "general") for doc in rag_result.documents))
                }
            
            return HotelInfoOutput(
                response=response,
                suggested_actions=suggested_actions,
                related_info=related_info,
                conversation_id=conversation_id,
                query_id=query_id,
                debug_info=debug_info
            )
            
        except Exception as e:
            logger.error(f"Error processing hotel information request: {e}", exc_info=True)
            return HotelInfoOutput(
                response=self.response_templates["error"],
                suggested_actions=["Contact hotel staff", "Try a different question"],
                query_id=query_id
            )
    
    async def _generate_llm_response(self, prompt: str) -> str:
        """Generate a response using an LLM service.
        
        Args:
            prompt: Prompt for the LLM
            
        Returns:
            Generated response
        """
        try:
            if self.llm_service:
                return await self.llm_service.generate(prompt)
            else:
                logger.warning("LLM service not available, falling back to template response")
                return "I'm sorry, but I'm currently operating with limited capabilities. " + \
                       "Please contact our hotel staff for more detailed information."
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}", exc_info=True)
            return self.response_templates["error"]
    
    def _generate_template_response(self, context: Dict[str, Any]) -> str:
        """Generate a response based on templates and context.
        
        Args:
            context: Context for response generation
            
        Returns:
            Generated response
        """
        query_type = context["query_type"]
        hotel_info = context["hotel_info"]
        guest_name = context["guest_name"]
        
        # Check if we have any hotel information
        if not hotel_info:
            template = self.response_templates["no_info"]
            return template.format(query_type=query_type, guest_name=guest_name)
        
        # Check for specific query type templates
        template_key = f"{query_type}_response" if f"{query_type}_response" in self.response_templates else "general_response"
        template = self.response_templates[template_key]
        
        # Format response
        return template.format(
            query_type=query_type,
            hotel_info=hotel_info,
            guest_name=guest_name
        )
    
    def _infer_query_type(self, message: str, documents: List[Document]) -> str:
        """Infer query type from message and retrieved documents.
        
        Args:
            message: User message
            documents: Retrieved documents
            
        Returns:
            Inferred query type
        """
        # First try to extract from message
        entities = self._extract_entities(message)
        if "entity_type" in entities:
            return entities["entity_type"]
        
        # Then try to infer from document categories
        if documents:
            # Count categories
            category_counts = {}
            for doc in documents:
                category = doc.metadata.get("category", "general")
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Get most common category
            if category_counts:
                return max(category_counts.items(), key=lambda x: x[1])[0]
        
        # Default to general
        return "general"
    
    def _generate_suggested_actions(self, query_type: str, documents: List[Document]) -> List[str]:
        """Generate suggested actions based on the query type and documents.
        
        Args:
            query_type: Type of query
            documents: Retrieved documents
            
        Returns:
            List of suggested actions
        """
        # Base suggestions by query type
        base_suggestions = {
            "rooms": [
                "Book a room",
                "View room amenities",
                "Request room service"
            ],
            "dining": [
                "Make a restaurant reservation",
                "View restaurant hours",
                "Order room service"
            ],
            "spa": [
                "Book a spa appointment",
                "View spa services",
                "Check spa hours"
            ],
            "check_in_out": [
                "View check-in/out times",
                "Request early check-in",
                "Request late check-out"
            ],
            "facilities": [
                "View pool hours",
                "Book fitness class",
                "Reserve meeting room"
            ],
            "general": [
                "Speak to a representative",
                "View hotel amenities",
                "View local attractions"
            ]
        }
        
        # Get base suggestions
        suggestions = base_suggestions.get(query_type, base_suggestions["general"]).copy()
        
        # Add document-specific suggestions
        doc_suggestions = set()
        for doc in documents[:3]:  # Use top 3 documents
            category = doc.metadata.get("category", "general")
            
            # Extract potential actions from document content
            if "check-in" in doc.content.lower() or "check-out" in doc.content.lower():
                doc_suggestions.add("View check-in/out policy")
            
            if "breakfast" in doc.content.lower() or "restaurant" in doc.content.lower():
                doc_suggestions.add("View dining options")
            
            if "wifi" in doc.content.lower() or "internet" in doc.content.lower():
                doc_suggestions.add("Get WiFi information")
            
            if "pool" in doc.content.lower() or "gym" in doc.content.lower():
                doc_suggestions.add("View facility hours")
            
            if "reservation" in doc.content.lower() or "book" in doc.content.lower():
                doc_suggestions.add("Make a reservation")
        
        # Add document suggestions
        for suggestion in doc_suggestions:
            if suggestion not in suggestions:
                suggestions.append(suggestion)
        
        # Limit to 5 suggestions
        return suggestions[:5]
    
    def _generate_related_info(self, query_type: str, documents: List[Document]) -> Dict[str, Any]:
        """Generate enhanced related information based on the query type and retrieved documents.
        
        Args:
            query_type: Type of query
            documents: Retrieved documents
            
        Returns:
            Dictionary of related information
        """
        related_info = {
            "category": query_type,
            "highlights": [],
            "related_categories": set()
        }
        
        # Extract highlights from documents
        for doc in documents[:5]:  # Use top 5 documents
            if "category" in doc.metadata:
                category = doc.metadata["category"]
                related_info["related_categories"].add(category)
                
                # Extract key sentences
                sentences = doc.content.split(". ")
                key_sentence = sentences[0] if sentences else doc.content[:100]
                
                highlight = {
                    "category": category,
                    "content": key_sentence + ("..." if len(key_sentence) < len(doc.content) else ""),
                    "sentiment": doc.metadata.get("sentiment", "neutral"),
                    "source": doc.metadata.get("source", "hotel_info")
                }
                related_info["highlights"].append(highlight)
        
        # Convert set to list for JSON serialization
        related_info["related_categories"] = list(related_info["related_categories"])
        
        return related_info
    
    async def submit_feedback(self, query_id: str, helpful: bool, comments: Optional[str] = None):
        """Submit feedback for a query to improve RAG performance.
        
        Args:
            query_id: ID of the query
            helpful: Whether the response was helpful
            comments: Optional comments
        """
        feedback = RAGFeedback(
            query_id=query_id,
            relevant=helpful,
            helpful=helpful,
            comments=comments
        )
        
        try:
            self.rag_module.add_feedback(feedback)
            logger.info(f"Submitted feedback for query {query_id}: helpful={helpful}")
            return True
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            return False