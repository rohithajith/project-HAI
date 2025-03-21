"""
FastAPI server for the Hotel AI Assistant multi-agent system.

This module implements a FastAPI server that exposes the LangGraph multi-agent system
as a REST API and WebSocket interface.
"""

import logging
import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .supervisor import create_hotel_supervisor
from .schemas import ConversationState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(
    title="Hotel AI Assistant API",
    description="API for the Hotel AI Assistant multi-agent system",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the LangGraph workflow
model_name = os.environ.get("LLM_MODEL", "gpt-4o")
supervisor_workflow = create_hotel_supervisor(model_name=model_name)
graph = supervisor_workflow.compile()

# Active conversations
active_conversations = {}


# Request and response models
class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the message sender (user or assistant)")
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="List of messages in the conversation")
    conversation_id: Optional[str] = Field(None, description="ID of the conversation")


class ChatResponse(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Updated list of messages in the conversation")
    conversation_id: str = Field(..., description="ID of the conversation")
    agent_outputs: Dict[str, Any] = Field(default_factory=dict, description="Outputs from the agents")


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, conversation_id: str):
        await websocket.accept()
        self.active_connections[conversation_id] = websocket
        logger.info(f"WebSocket connection established for conversation: {conversation_id}")

    def disconnect(self, conversation_id: str):
        if conversation_id in self.active_connections:
            del self.active_connections[conversation_id]
            logger.info(f"WebSocket connection closed for conversation: {conversation_id}")

    async def send_message(self, conversation_id: str, message: Dict[str, Any]):
        if conversation_id in self.active_connections:
            await self.active_connections[conversation_id].send_json(message)
            logger.info(f"Message sent to conversation: {conversation_id}")


manager = ConnectionManager()


# API endpoints
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message using the multi-agent system."""
    try:
        # Get or create conversation ID
        conversation_id = request.conversation_id or f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}_{id(request)}"
        
        # Convert messages to the format expected by the LangGraph workflow
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Get or create conversation state
        if conversation_id in active_conversations:
            # Update existing conversation
            state = active_conversations[conversation_id]
            state["messages"] = messages
        else:
            # Create new conversation
            state = {
                "messages": messages,
                "current_agent": None,
                "agent_outputs": {}
            }
        
        # Process the message with the LangGraph workflow
        result = await graph.ainvoke(state)
        
        # Update the active conversation
        active_conversations[conversation_id] = result
        
        # Convert the result back to the API response format
        response_messages = [ChatMessage(role=msg["role"], content=msg["content"]) for msg in result["messages"]]
        
        return ChatResponse(
            messages=response_messages,
            conversation_id=conversation_id,
            agent_outputs=result["agent_outputs"]
        )
    
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat message: {str(e)}")


@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    """WebSocket endpoint for real-time chat."""
    await manager.connect(websocket, conversation_id)
    try:
        while True:
            # Receive message from the client
            data = await websocket.receive_text()
            
            try:
                # Parse the message
                message_data = json.loads(data)
                
                # Extract the message
                if "message" not in message_data:
                    await websocket.send_json({"error": "Invalid message format"})
                    continue
                
                user_message = message_data["message"]
                
                # Get or create conversation state
                if conversation_id in active_conversations:
                    # Update existing conversation
                    state = active_conversations[conversation_id]
                    state["messages"].append({"role": "user", "content": user_message})
                else:
                    # Create new conversation
                    state = {
                        "messages": [{"role": "user", "content": user_message}],
                        "current_agent": None,
                        "agent_outputs": {}
                    }
                
                # Process the message with the LangGraph workflow
                result = await graph.ainvoke(state)
                
                # Update the active conversation
                active_conversations[conversation_id] = result
                
                # Send the response back to the client
                await websocket.send_json({
                    "messages": result["messages"],
                    "agent_outputs": result["agent_outputs"]
                })
            
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON"})
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await websocket.send_json({"error": f"Error processing message: {str(e)}"})
    
    except WebSocketDisconnect:
        manager.disconnect(conversation_id)


@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a conversation by ID."""
    if conversation_id not in active_conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    state = active_conversations[conversation_id]
    
    return {
        "messages": state["messages"],
        "agent_outputs": state["agent_outputs"]
    }


@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation by ID."""
    if conversation_id in active_conversations:
        del active_conversations[conversation_id]
    
    return {"status": "success"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Main entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)