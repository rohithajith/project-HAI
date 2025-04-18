from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from typing import List, Dict, Optional
from ai_agents.agent_manager import AgentManager
from ai_agents.conversation_memory import ConversationMemory
from datetime import datetime
import logging
import uvicorn
import socket
import socketio
import json
from starlette.routing import Mount
from starlette.applications import Starlette
from data_protection import data_protection_manager, start_scheduled_tasks

# -------------------- Logger Setup --------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------- Core FastAPI Setup --------------------
app = FastAPI()
agent_manager = AgentManager()

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Socket.IO Setup --------------------
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
sio_app = socketio.ASGIApp(sio)

# -------------------- Mount FastAPI to Starlette --------------------
combined_app = Starlette(
    routes=[Mount("/", app)],
    on_startup=[lambda: logger.info("🚀 App mounted!")],
)

# Start data protection scheduled tasks
start_scheduled_tasks()
logger.info("🔒 Data protection tasks initialized")

socket_app = socketio.ASGIApp(sio, other_asgi_app=combined_app)

@app.get("/")
async def root():
    return {"message": "Welcome to the Socket.IO FastAPI server"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

class Message(BaseModel):
    content: str
    history: List[Dict[str, str]] = []
    
class ConsentUpdate(BaseModel):
    status: str  # "granted", "denied", "withdrawn"
    purposes: Optional[List[str]] = None
    
class DataUpdateRequest(BaseModel):
    content: str

@app.post("/chat")
async def chat(message: Message):
    try:
        logger.info(f"📥 REST message: {message.content}")
        response = agent_manager.process(message.content, message.history)
        return response
    except Exception as e:
        logger.error(f"REST Error: {e}", exc_info=True)
        # Use agent_manager's handle_error method which includes filtering
        return agent_manager.handle_error(e)

@sio.event
async def connect(sid, environ):
    logger.info(f"✅ Client connected: {sid}")

@sio.event
async def disconnect(sid):
    logger.info(f"❌ Client disconnected: {sid}")

@sio.event
async def guest_message(sid, data):
    try:
        logger.info(f"📩 guest_message from {sid}: {data}")
        user_input = data.get("content", "")
        history = data.get("history", [])
        room = data.get("room", "unknown")

        response = agent_manager.process(user_input, history)
        agent_raw = response.get("agent", "Unknown")
        agent_name = agent_raw.replace(" ", "") + "Agent"

        message = {
            "response": response.get("response", ""),
            "tool_calls": response.get("tool_calls", []),
            "timestamp": response.get("timestamp", datetime.now().isoformat()),
            "agent": agent_name,
            "room": room,
            "type": response.get("tool_calls", [{}])[0].get("request_type", "Room Service"),
            "status": "Pending",
            "time": datetime.now().strftime("%I:%M %p")
        }

        logger.info(f"📡 Broadcasting to all clients: {message}")
        await sio.emit("guest_response", message)

    except Exception as e:
        logger.error(f"Socket Error: {e}", exc_info=True)
        # Use agent_manager's handle_error method which includes filtering
        error_response = agent_manager.handle_error(e)
        await sio.emit("guest_response", {
            "response": error_response["response"],
            "tool_calls": error_response["tool_calls"],
            "timestamp": error_response["timestamp"],
            "agent": error_response["agent"],
            "room": data.get("room", "unknown"),
            "type": "Error",
            "status": "Error",
            "time": datetime.now().strftime("%I:%M %p")
        })

@sio.event
async def request_completed(sid, data):
    logger.info(f"✅ Request marked as completed via dashboard: {data}")
    data["status"] = "Completed"
    await sio.emit("guest_response", data)

@sio.event
# -------------------- GDPR Compliance Endpoints --------------------
@app.get("/api/privacy/notice")
async def get_privacy_notice():
    """Return the privacy notice with consent options"""
    return {
        "title": "Privacy Notice",
        "content": (
            "This AI assistant collects and processes your conversation data to provide hotel services. "
            "Your data is anonymized and stored securely. "
            "You have the right to access, correct, or delete your data at any time. "
            "We retain conversation data for 90 days after your last interaction. "
            "For more information, please see our full privacy policy."
        ),
        "consent_options": [
            {"id": "customer_service", "label": "Process data to provide customer service", "required": True},
            {"id": "service_improvement", "label": "Use data to improve our services", "required": False},
            {"id": "marketing", "label": "Send personalized offers and promotions", "required": False}
        ],
        "buttons": [
            {"id": "accept_all", "label": "Accept All"},
            {"id": "accept_required", "label": "Accept Only Required"},
            {"id": "reject_all", "label": "Reject All"}
        ]
    }

@app.get("/api/user/data/{conversation_id}")
async def get_user_data(conversation_id: str):
    """Allow users to access their data (Right of Access)"""
    memory = ConversationMemory()
    if memory.load_conversation(conversation_id):
        # Return the conversation data
        return {
            "conversation_id": memory.conversation_id,
            "messages": memory.conversation_history,
            "gdpr_metadata": {
                "purposes": memory.data_purposes,
                "consent_status": memory.consent_status,
                "retention_period": memory.retention_period
            }
        }
    raise HTTPException(status_code=404, detail="Conversation not found")

@app.delete("/api/user/data/{conversation_id}")
async def delete_user_data(conversation_id: str):
    """Allow users to delete their data (Right to Erasure)"""
    memory = ConversationMemory()
    if memory.load_conversation(conversation_id):
        if memory.delete_data():
            return {"status": "Data deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete data")
    raise HTTPException(status_code=404, detail="Conversation not found")

@app.put("/api/user/data/{conversation_id}/{message_id}")
async def update_user_data(conversation_id: str, message_id: str, update: DataUpdateRequest):
    """Allow users to correct their data (Right to Rectification)"""
    memory = ConversationMemory()
    if memory.load_conversation(conversation_id):
        # Find and update the specific message
        for message in memory.conversation_history:
            if message.get("id") == message_id:
                # Only allow updating user messages
                if message.get("role") == "user":
                    # Anonymize the new content
                    anonymized_content = memory._anonymize_personal_data(update.content)
                    message["content"] = anonymized_content
                    message["updated_at"] = datetime.now().isoformat()
                    # Save the updated conversation
                    memory._save_conversation()
                    return {"status": "Data updated successfully"}
                else:
                    raise HTTPException(status_code=403, detail="Can only update user messages")
        raise HTTPException(status_code=404, detail="Message not found")
    raise HTTPException(status_code=404, detail="Conversation not found")

@app.post("/api/user/consent/{conversation_id}")
async def update_consent(conversation_id: str, consent: ConsentUpdate):
    """Update user consent preferences"""
    memory = ConversationMemory()
    if memory.load_conversation(conversation_id):
        if memory.update_consent(consent.status, consent.purposes):
            return {"status": "Consent updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update consent")
    raise HTTPException(status_code=404, detail="Conversation not found")

@app.get("/api/user/data/export/{conversation_id}")
async def export_user_data(conversation_id: str):
    """Export all user data in a portable format (Right to Data Portability)"""
    memory = ConversationMemory()
    if memory.load_conversation(conversation_id):
        # Create a portable format (JSON)
        portable_data = {
            "conversation_id": memory.conversation_id,
            "created_at": next((msg.get("timestamp") for msg in memory.conversation_history if msg), None),
            "messages": [
                {
                    "role": msg.get("role"),
                    "content": msg.get("content"),
                    "timestamp": msg.get("timestamp")
                }
                for msg in memory.conversation_history
                if msg.get("role") == "user"  # Only include user messages
            ]
        }
        
        # Set response headers for file download
        headers = {
            'Content-Disposition': f'attachment; filename="conversation_{conversation_id}.json"'
        }
        
        return Response(
            content=json.dumps(portable_data, indent=2),
            media_type="application/json",
            headers=headers
        )
    raise HTTPException(status_code=404, detail="Conversation not found")
async def rating_feedback(sid, data):
    logger.info(f"⭐ Rating received: {data}")
    await sio.emit("rating_feedback", data)

# -------------------- Dynamic Port Picker --------------------
def find_available_port(start_port: int, max_port: int) -> int:
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except socket.error:
                continue
    raise RuntimeError(f"No available ports in range {start_port}-{max_port}")

# -------------------- Entry Point --------------------
if __name__ == "__main__":
    try:
        port = find_available_port(8000, 8020)
        logger.info(f"🚀 Starting server at http://localhost:{port}")
        uvicorn.run(socket_app, host="0.0.0.0", port=port)
    except Exception as e:
        logger.error(f"❌ Failed to start server: {str(e)}", exc_info=True)
