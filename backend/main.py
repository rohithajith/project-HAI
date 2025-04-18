from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from ai_agents.agent_manager import AgentManager
from datetime import datetime
import logging
import uvicorn
import socket
import socketio
from starlette.routing import Mount
from starlette.applications import Starlette

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
