#!/bin/bash
# Run agent tests with pytest

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Navigate to backend directory
cd "$(dirname "$0")"

# Install requirements if not already installed
pip install -r requirements.txt

# Run pytest with asyncio support
python -m pytest test_agents.py -v

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi