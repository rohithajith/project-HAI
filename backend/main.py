import os
import sys
import logging
import threading
import uvicorn
from flask_app import start_flask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("main")

def start_fastapi():
    """Start the FastAPI server"""
    logger.info("Starting FastAPI server...")
    uvicorn.run("fastapi_server:app", host="0.0.0.0", port=8001, reload=False)

def main():
    """Start both FastAPI and Flask servers"""
    logger.info("Starting Hotel AI Backend...")
    
    # Start FastAPI in a separate thread
    fastapi_thread = threading.Thread(target=start_fastapi)
    fastapi_thread.daemon = True
    fastapi_thread.start()
    
    # Start Flask in the main thread
    logger.info("Starting Flask server...")
    start_flask()

if __name__ == "__main__":
    main()