#!/usr/bin/env python
"""
Chatbot Bridge Script for Hotel Management System

This script serves as a bridge between the Node.js backend and the local model.
It receives chat messages from the backend, processes them using the local model,
and returns the response.

Usage:
    python chatbot_bridge.py --message "User message" [--history "JSON history string"]

Requirements:
    - torch
    - transformers
"""

import argparse
import json
import os
import sys
import logging
from pathlib import Path
from local_model_chatbot import process_message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("chatbot_bridge")

# System prompt for the hotel AI assistant
SYSTEM_PROMPT = "you are a helpfull hotel ai which acts like hotel reception udating requests and handiling queries from users"

def main():
    """Main function to parse arguments and process the message"""
    parser = argparse.ArgumentParser(description="Chatbot bridge for local model")
    parser.add_argument("--message", required=True, help="User message")
    parser.add_argument("--history", help="JSON string of conversation history")
    
    args = parser.parse_args()
    
    result = process_message(args.message, args.history)
    print(json.dumps(result))

if __name__ == "__main__":
    main()