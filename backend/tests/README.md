# AI Agents Test Suite

## Overview
This comprehensive test suite provides in-depth testing for the AI Agents in the hotel management system. It covers multiple dimensions of agent functionality to ensure robust and reliable performance.

## Test Categories

### 1. Agent Functionality Tests (`@agent_test`)
- Agent Manager Initialization
- Input Filtering
- Emergency Detection
- Service Handling
- Conversation Memory
- Tool Call Capabilities

### 2. Performance Tests (`@performance_test`)
- Response Time Measurement
- Load Handling Checks

### 3. Specific Agent Tests
- SOS Agent
- Room Service Agent
- Maintenance Agent
- Wellness Agent
- Service Booking Agent
- Check-in Agent
- Supervisor Agent

## Prerequisites

### System Requirements
- Python 3.8+
- pytest
- pytest-cov (for coverage reporting)

### Installation
1. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

## Running Tests

### Basic Test Execution
```bash
# Run all tests
pytest test_ai_agents.py

# Verbose output
pytest -v test_ai_agents.py
```

### Specific Test Categories
```bash
# Run only agent functionality tests
pytest -v -m agent_test

# Run performance tests
pytest -v -m performance_test

# Run slow tests (requires --runslow flag)
pytest --runslow
```

### Generate Coverage Report
```bash
pytest --cov=backend/ai_agents test_ai_agents.py
```

## Test Configuration

### Markers
- `agent_test`: Core agent functionality tests
- `performance_test`: Load and response time tests
- `slow`: Tests that take longer to execute

## Debugging Tips
- Use `-v` for verbose output
- Use `-s` to see print statements
- Use `--pdb` to drop into debugger on test failure

## Customization
- Add new test cases in `test_ai_agents.py`
- Ensure all new functionality is comprehensively tested
- Maintain existing test structure and conventions

## Best Practices
1. Keep tests focused and specific
2. Test both positive and negative scenarios
3. Mock external dependencies
4. Ensure tests are independent and repeatable

## Troubleshooting
- Ensure all dependencies are installed
- Check Python and pytest versions
- Verify project root is in Python path

## Contributing
- Follow existing test patterns
- Add docstrings to new test methods
- Maintain high code coverage
- Write clear, concise test cases