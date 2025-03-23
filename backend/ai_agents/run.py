#!/usr/bin/env python
"""
Run script for the Hotel AI Assistant FastAPI server.

This script starts the FastAPI server for the Hotel AI Assistant.
"""

import os
import sys
import logging
import uvicorn
from dotenv import load_dotenv

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.environ.get("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Get configuration
port = int(os.environ.get("PORT", 8001))
host = os.environ.get("HOST", "0.0.0.0")
reload = os.environ.get("DEBUG", "False").lower() == "true"

if __name__ == "__main__":
    logger.info(f"Starting Hotel AI Assistant server on {host}:{port}")
    logger.info(f"Debug mode: {reload}")
    
    # Check if OpenAI API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY environment variable is not set")
    
    # Start the server
    uvicorn.run(
        "backend.ai_agents.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level=os.environ.get("LOG_LEVEL", "info").lower()
    )