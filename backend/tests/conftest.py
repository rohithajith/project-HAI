import os
import sys
import pytest

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def pytest_configure(config):
    """
    Configure pytest settings for AI agent testing
    """
    # Set custom markers
    config.addinivalue_line(
        "markers", 
        "agent_test: mark a test as an AI agent functionality test"
    )
    config.addinivalue_line(
        "markers", 
        "performance_test: mark a test related to performance and load testing"
    )
    config.addinivalue_line(
        "markers", 
        "slow: mark test as slow to run"
    )

def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add custom behaviors
    """
    for item in items:
        if "agent_test" in item.keywords:
            item.add_marker(pytest.mark.agent_test)
        if "performance_test" in item.keywords:
            item.add_marker(pytest.mark.performance_test)
        if "slow" in item.keywords:
            item.add_marker(pytest.mark.skip(reason="need --runslow option to run"))

@pytest.fixture(scope="session")
def mock_model():
    """
    Fixture to provide a mock model for testing
    """
    from unittest.mock import Mock
    mock_model = Mock()
    mock_model.generate.return_value = Mock()
    return mock_model

@pytest.fixture(scope="session")
def mock_tokenizer():
    """
    Fixture to provide a mock tokenizer for testing
    """
    from unittest.mock import Mock
    mock_tokenizer = Mock()
    mock_tokenizer.encode.return_value = [1, 2, 3]
    mock_tokenizer.decode.return_value = "Test response"
    return mock_tokenizer

@pytest.fixture
def conversation_memory():
    """
    Fixture to provide a fresh ConversationMemory for each test
    """
    from backend.ai_agents.conversation_memory import ConversationMemory
    return ConversationMemory()

def pytest_addoption(parser):
    """
    Add custom command-line options for testing
    """
    parser.addoption(
        "--runslow", 
        action="store_true", 
        default=False, 
        help="run slow tests"
    )