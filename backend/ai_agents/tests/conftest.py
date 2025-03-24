"""
Configuration file for pytest.

This file is automatically loaded by pytest and can be used to add fixtures
and configure the test environment.
"""

import os
import sys
import pytest

# Add the parent directory to the Python path so that we can import modules
# from the backend/ai_agents directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import modules from the backend/ai_agents directory
# For example:
# from rag.vector_store import VectorStore
# from agents.base_agent import BaseAgent