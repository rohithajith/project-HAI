import os
import sys
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("fastapi_server")

# Add path to backend directory to import ai_agents
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import agent manager
try:
    from ai_agents.agent_manager import AgentManagerCorrected
    from ai_agents.base_agent import AgentOutput
    # Instantiate Agent Manager
    agent_manager = AgentManagerCorrected()
    logger.info("Agent Manager initialized.")
except ImportError as e:
    logger.error(f"Failed to import agent modules: {e}")
    logger.error("Ensure agents are correctly placed and PYTHONPATH is set if needed.")
    agent_manager = None
except Exception as e:
    logger.error(f"Error initializing Agent Manager: {e}")
    agent_manager = None

# Create FastAPI app
app = FastAPI(title="Hotel AI Backend")

# Message model
class ChatMessage(BaseModel):
    message: str
    history: Optional[List[Dict[str, Any]]] = []

# Process message and handle notifications
async def process_message_with_agents(message: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process a message using agents and handle notifications."""
    try:
        if not agent_manager:
            return {
                "response": "Agent system is not available at the moment.",
                "notifications": []
            }
        
        # Process message with agent manager
        agent_output = await agent_manager.process(message, history)
        
        if agent_output and (agent_output.response or agent_output.tool_used):
            # Agent handled the request
            return {
                "response": agent_output.response or "Your request is being processed.",
                "notifications": agent_output.notifications or []
            }
        else:
            # No agent handled the request
            return {
                "response": "I'm not sure how to help with that specific request.",
                "notifications": []
            }
    except Exception as e:
        logger.exception(f"Error processing message: {e}")
        return {
            "response": "An error occurred while processing your request.",
            "notifications": []
        }

# HTTP endpoints
@app.get("/")
async def root():
    return {"message": "Hotel AI Backend API"}

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "agent_manager": "available" if agent_manager else "unavailable"
    }

@app.post("/api/message")
async def process_message(message: ChatMessage):
    """Process a message via HTTP endpoint"""
    result = await process_message_with_agents(message.message, message.history)
    return result

# Mount static files for frontend (will be added later)
# app.mount("/", StaticFiles(directory="../frontend/build", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_server:app", host="0.0.0.0", port=8001, reload=True)