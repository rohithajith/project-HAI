from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from ai_agents.agent_manager import AgentManager
import logging
import uvicorn
import socket

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
agent_manager = AgentManager()

class Message(BaseModel):
    content: str
    history: List[Dict[str, str]] = []

@app.post("/chat")
async def chat(message: Message):
    try:
        logger.info(f"Received message: {message.content}")
        response = agent_manager.process(message.content, message.history)
        logger.info(f"Generated response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        error_response = agent_manager.handle_error(e)
        return error_response

@app.get("/health")
async def health_check():
    return {"status": "ok"}

def find_available_port(start_port: int, max_port: int) -> int:
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except socket.error:
                continue
    raise RuntimeError(f"No available ports in range {start_port}-{max_port}")

if __name__ == "__main__":
    try:
        port = find_available_port(8000, 8020)
        logger.info(f"Starting the server on port {port}...")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        logger.error(f"Failed to start the server: {str(e)}", exc_info=True)