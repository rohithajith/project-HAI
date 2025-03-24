#!/usr/bin/env python
"""
Run script for the Hotel AI agents.

This script provides a command-line interface to run the various agents
in the Hotel AI system.
"""

import os
import sys
import json
import logging
import argparse
import asyncio
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run Hotel AI agents")
    parser.add_argument("--agent", required=True, help="Agent to run")
    parser.add_argument("--input", help="JSON input for the agent")
    return parser.parse_args()

async def run_hotel_info_agent(input_data: Dict[str, Any]):
    """Run the hotel information agent.
    
    Args:
        input_data: Input data for the agent
        
    Returns:
        Agent output
    """
    try:
        from agents.hotel_info_agent import HotelInfoAgent, HotelInfoInput
        from schemas.message import Message
        
        # Create input object
        messages = []
        if "messages" in input_data:
            for msg in input_data["messages"]:
                messages.append(Message(
                    sender=msg.get("role", "user"),
                    content=msg.get("content", "")
                ))
        
        # Add latest message if not in messages
        if "latest_message" in input_data and input_data["latest_message"]:
            messages.append(Message(
                sender="user",
                content=input_data["latest_message"]
            ))
        
        agent_input = HotelInfoInput(
            guest_name=input_data.get("guest_name"),
            booking_id=input_data.get("booking_id"),
            messages=messages,
            query_type=input_data.get("query_type")
        )
        
        # Run agent
        agent = HotelInfoAgent()
        result = await agent.process(agent_input)
        
        # Return result as JSON
        return result.dict()
    except Exception as e:
        logger.exception(f"Error running hotel info agent: {e}")
        return {"error": str(e)}

async def run_rag_status():
    """Check the status of the RAG module.
    
    Returns:
        Status information
    """
    try:
        from rag.rag_module import RAGModule
        from rag.vector_store import VectorStore
        
        # Initialize components
        vector_store = VectorStore()
        rag_module = RAGModule()
        
        # Get status information
        status = {
            "initialized": vector_store.index is not None,
            "document_count": vector_store.index.ntotal if vector_store.index else 0,
            "embedding_dimension": vector_store.embedding_dim,
            "categories": {}
        }
        
        # Count documents by category
        for doc_id, doc in vector_store.documents.items():
            category = doc.metadata.get("category", "unknown")
            if category not in status["categories"]:
                status["categories"][category] = 0
            status["categories"][category] += 1
        
        return status
    except Exception as e:
        logger.exception(f"Error checking RAG status: {e}")
        return {"error": str(e)}

async def main():
    """Main function."""
    args = parse_args()
    
    # Determine which agent to run
    if args.agent == "hotel_info":
        if not args.input:
            logger.error("Input is required for hotel_info agent")
            sys.exit(1)
        
        try:
            input_data = json.loads(args.input)
            result = await run_hotel_info_agent(input_data)
            print(json.dumps(result))
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON input: {args.input}")
            sys.exit(1)
    elif args.agent == "rag_status":
        result = await run_rag_status()
        print(json.dumps(result))
    else:
        logger.error(f"Unknown agent: {args.agent}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())