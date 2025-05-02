from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import socketio
import uvicorn
import sys
import os
import json
from backend.ai_agents.agent_manager import AgentManager


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')

app = FastAPI()
sio_app = socketio.ASGIApp(sio, other_asgi_app=app)

# === CORS Middleware ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Agent Manager ===
agent_manager = AgentManager()

# === Socket.IO Events ===
@sio.event
async def connect(sid, environ):
    print("✅ Socket connected:", sid)

@sio.event
async def disconnect(sid):
    print("❌ Socket disconnected:", sid)

@sio.event
async def guest_message(sid, data):
    try:
        print(f"📩 Received guest message: {data}")
        content = data.get("content", "")
        room = data.get("room", "")

        # Notify frontend that AI is typing
        await sio.emit("ai_typing", {"room": room})

        # Process message
        response = agent_manager.process(content)
        response["room"] = room
        response["status"] = "Pending"
        response["original_request"] = content 

        print("📤 Emitting guest_response")
        await sio.emit("guest_response", json.loads(json.dumps(response, ensure_ascii=False)))

    except Exception as e:
        print("❌ Error in guest_message:", str(e))

@sio.event
async def request_completed(sid, data):
    try:
        print(f"✅ Request marked as completed: {data}")
        await sio.emit("guest_response", {
            **data,
            "status": "Completed"
        })
    except Exception as e:
        print("❌ Error in request_completed:", str(e))

@sio.event
async def rating_feedback(sid, data):
    try:
        print(f"⭐ Received rating: {data}")
        await sio.emit("rating_feedback", data)
    except Exception as e:
        print("❌ Error in rating_feedback:", str(e))


class ChatRequest(BaseModel):
    content: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response = agent_manager.process(request.content)
        response["room"] = "101"
        response["status"] = "Pending"
        await sio.emit("guest_response", json.loads(json.dumps(response, ensure_ascii=False)))
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    uvicorn.run("backend.main:sio_app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()