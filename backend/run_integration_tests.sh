#!/bin/bash
# Run integration tests for Hotel AI

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Navigate to backend directory
cd "$(dirname "$0")"

# Install requirements
pip install -r requirements.txt

# Run integration tests with verbose output
python -m pytest test_integration.py -v

# Generate integration test report
python -c "import test_integration; test_integration.pytest_configure(None)"

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi