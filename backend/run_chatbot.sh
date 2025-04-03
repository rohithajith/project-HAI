#!/bin/bash
# Script to run the separate guest chatbot

# Change to the project root directory
cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the chatbot application
python backend/run_chatbot.py