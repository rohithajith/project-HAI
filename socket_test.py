from fastapi import FastAPI
from fastapi_socketio import SocketManager

app = FastAPI()
socket_manager = SocketManager(app=app, cors_allowed_origins="*")

@socket_manager.on("connect")
async def handle_connect(sid, *args, **kwargs):
    print("✅ Connected to Socket.IO:", sid)

@socket_manager.on("test_event")
async def handle_test(sid, data):
    print("📩 Got from client:", data)
    await socket_manager.emit("test_response", {"msg": "Hello from backend!"}, room=sid)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
