"""
Hotel Information Agent for the Hotel AI system.

This agent specializes in providing information about the hotel,
leveraging the RAG module for accurate and contextual responses.
"""

import logging
from typing import Dict, Any, Optional, List
import json

from .base_agent import BaseAgent
from ..schemas.message import Message
from ..schemas.agent_io import AgentInput, AgentOutput
from ..rag.rag_module import RAGQuery
from ..rag.vector_store import Document

logger = logging.getLogger(__name__)

class HotelInfoInput(AgentInput):
    """Input for the hotel information agent."""
    guest_name: Optional[str] = None
    booking_id: Optional[str] = None
    messages: List[Message] = []
    query_type: Optional[str] = None  # e.g., "room", "dining", "spa", "general"

class HotelInfoOutput(AgentOutput):
    """Output from the hotel information agent."""
    response: str
    suggested_actions: List[str] = []
    related_info: Optional[Dict[str, Any]] = None

class HotelInfoAgent(BaseAgent):
    """Agent for providing hotel information."""
    
    def __init__(self):
        """Initialize the hotel information agent."""
        super().__init__("HotelInfoAgent")
        logger.info("Hotel Information Agent initialized")
    
    async def process(self, input_data: HotelInfoInput) -> HotelInfoOutput:
        """Process a hotel information request.
        
        Args:
            input_data: The hotel information request data
            
        Returns:
            The hotel information response
        """
        logger.info(f"Processing hotel information request: {input_data.query_type}")
        
        # Extract the latest user message
        latest_message = input_data.messages[-1].content if input_data.messages else ""
        
        # Create state for RAG processing
        state = {
            "booking_id": input_data.booking_id,
            "guest_name": input_data.guest_name,
            "query_type": input_data.query_type,
            "messages": [{"role": m.sender, "content": m.content} for m in input_data.messages]
        }
        
        # Process with RAG
        rag_result = await self.rag_module.process_query(
            RAGQuery(query=latest_message, context=state)
        )
        state["rag_context"] = rag_result.context
        
        # Extract entities from the message
        entities = self._extract_entities(latest_message)
        
        # Prepare context for response generation
        context = {
            "guest_name": input_data.guest_name or "Guest",
            "booking_id": input_data.booking_id,
            "query_type": input_data.query_type or entities.get("entity_type", "general"),
            "conversation_history": "\n".join([f"{m.sender}: {m.content}" for m in input_data.messages[:-1]]),
            "latest_message": latest_message,
            "hotel_info": state.get("rag_context", "")
        }
        
        # Generate response based on context
        response = self._generate_response(context)
        
        # Generate suggested actions based on the query type
        suggested_actions = self._generate_suggested_actions(context["query_type"])
        
        # Generate related information
        related_info = self._generate_related_info(context["query_type"], rag_result.documents)
        
        return HotelInfoOutput(
            response=response,
            suggested_actions=suggested_actions,
            related_info=related_info
        )
    
    def _generate_response(self, context: Dict[str, Any]) -> str:
        """Generate a response based on the context.
        
        Args:
            context: Context for response generation
            
        Returns:
            Generated response
        """
        # This is a placeholder for actual LLM-based response generation
        # In a real implementation, this would use an LLM with the RAG context
        
        query_type = context["query_type"]
        hotel_info = context["hotel_info"]
        
        if not hotel_info:
            return f"I don't have specific information about {query_type} at the moment. Please contact the front desk for assistance."
        
        # Simple response based on the RAG context
        return f"Here's what I found about {query_type}:\n\n{hotel_info}"
    
    def _generate_suggested_actions(self, query_type: str) -> List[str]:
        """Generate suggested actions based on the query type.
        
        Args:
            query_type: Type of query
            
        Returns:
            List of suggested actions
        """
        suggestions = {
            "room": [
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
            "general": [
                "Speak to a representative",
                "View hotel amenities",
                "View local attractions"
            ]
        }
        
        return suggestions.get(query_type, suggestions["general"])
    
    def _generate_related_info(self, query_type: str, documents: List[Document]) -> Dict[str, Any]:
        """Generate related information based on the query type and retrieved documents.
        
        Args:
            query_type: Type of query
            documents: Retrieved documents
            
        Returns:
            Dictionary of related information
        """
        related_info = {
            "category": query_type,
            "highlights": []
        }
        
        # Extract highlights from documents
        for doc in documents[:3]:  # Use top 3 documents
            if "category" in doc.metadata:
                highlight = {
                    "category": doc.metadata["category"],
                    "content": doc.content[:100] + "..." if len(doc.content) > 100 else doc.content
                }
                related_info["highlights"].append(highlight)
        
        return related_info