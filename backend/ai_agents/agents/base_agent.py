"""
Base agent class for the Hotel AI system.

This module provides a base agent class that all other agents inherit from.
It includes RAG capabilities for enhanced responses.
"""

import logging
from typing import Dict, Any, Optional, List
import asyncio

from ..rag.rag_module import RAGModule, RAGQuery, RAGResult

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base agent class with RAG capabilities."""
    
    def __init__(self, name: str):
        """Initialize the base agent.
        
        Args:
            name: Name of the agent
        """
        self.name = name
        self.rag_module = RAGModule()
        logger.info(f"Initialized {name} with RAG capabilities")
    
    async def process_message(self, message: str, state: Dict[str, Any]) -> str:
        """Process a message with RAG enhancement.
        
        Args:
            message: User message to process
            state: Current conversation state
            
        Returns:
            Agent response
        """
        # Enhance with RAG if needed
        if self._should_use_rag(message, state):
            # Process with RAG
            rag_result = await self.rag_module.process_query(
                RAGQuery(query=message, context=state)
            )
            
            # Add RAG context to state
            state["rag_context"] = rag_result.context
            logger.info(f"Enhanced message with RAG context: {len(rag_result.context)} chars")
        
        # Implement in subclasses
        raise NotImplementedError("Subclasses must implement this method")
    
    def _should_use_rag(self, message: str, state: Dict[str, Any]) -> bool:
        """Determine if RAG should be used for this message.
        
        Args:
            message: User message
            state: Current conversation state
            
        Returns:
            True if RAG should be used, False otherwise
        """
        # Simple heuristic: use RAG for longer messages or questions
        return len(message) > 20 or "?" in message
    
    def _format_rag_context(self, context: str) -> str:
        """Format RAG context for inclusion in prompts.
        
        Args:
            context: RAG context
            
        Returns:
            Formatted context
        """
        if not context:
            return ""
        
        return f"\n\nRelevant Hotel Information:\n{context}\n"
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities from a message.
        
        This is a placeholder for more sophisticated entity extraction.
        
        Args:
            message: User message
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        
        # Simple keyword-based entity extraction
        if "room" in message.lower():
            entities["entity_type"] = "room"
        elif "restaurant" in message.lower() or "dining" in message.lower():
            entities["entity_type"] = "dining"
        elif "spa" in message.lower():
            entities["entity_type"] = "spa"
        elif "check" in message.lower() and ("in" in message.lower() or "out" in message.lower()):
            entities["entity_type"] = "check_in_out"
        
        return entities