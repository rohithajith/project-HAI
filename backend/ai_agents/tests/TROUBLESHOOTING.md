# Troubleshooting Guide for Hotel AI Tests

This guide provides solutions for common issues encountered when running the tests for the Hotel AI system.

## Import Errors

### Issue: ModuleNotFoundError: No module named 'agents' or 'rag'

```
ImportError while importing test module '...'.
ModuleNotFoundError: No module named 'agents'
```

**Solution:**

1. Install the package in development mode:

```bash
cd backend/ai_agents
pip install -e .
```

2. Make sure you're running the tests from the correct directory:

```bash
cd backend/ai_agents
python run_tests.py
```

3. If the issue persists, try setting the PYTHONPATH environment variable:

```bash
# On Windows
set PYTHONPATH=C:\path\to\project-HAI\backend\ai_agents
# On Linux/Mac
export PYTHONPATH=/path/to/project-HAI/backend/ai_agents
```

### Issue: ImportError: cannot import name 'BaseAgent' from 'backend.ai_agents.agents'

```
ImportError: cannot import name 'BaseAgent' from 'backend.ai_agents.agents'
```

**Solution:**

This error occurs when the `BaseAgent` class is not found in the agents module. Make sure the `base_agent.py` file exists and contains the `BaseAgent` class.

1. Check that the file exists:

```bash
ls backend/ai_agents/agents/base_agent.py
```

2. Make sure the class is defined correctly:

```python
# backend/ai_agents/agents/base_agent.py
class BaseAgent:
    # ...
```

3. Make sure the class is imported correctly in the agents/__init__.py file:

```python
# backend/ai_agents/agents/__init__.py
from .base_agent import BaseAgent
```

## Test Failures

### Issue: Tests fail with assertion errors

```
AssertionError: assert ... == ...
```

**Solution:**

1. Check the test output to see which assertion failed
2. Look at the expected and actual values
3. Update the code or the test as needed

### Issue: Tests fail with timeout errors

```
asyncio.TimeoutError: ...
```

**Solution:**

1. Increase the timeout in the test:

```python
@pytest.mark.asyncio
async def test_something():
    # Increase the timeout
    async with asyncio.timeout(10):  # 10 seconds instead of the default
        # Test code here
```

2. Check if the code is hanging or taking too long to execute

## Coverage Issues

### Issue: Coverage report shows low coverage

**Solution:**

1. Run the tests with coverage:

```bash
python run_tests.py --coverage
```

2. Check the coverage report to see which lines are not covered
3. Add tests for the uncovered lines

## Mock Issues

### Issue: Tests fail because mocks are not working correctly

```
AssertionError: Expected 'mock_method' to have been called once. Called 0 times.
```

**Solution:**

1. Check that the mock is created correctly
2. Check that the mock is patched in the right place
3. Check that the mock is used correctly in the test

## Environment Issues

### Issue: Tests fail because of missing dependencies

```
ImportError: No module named 'some_module'
```

**Solution:**

1. Install the missing dependency:

```bash
pip install some_module
```

2. Make sure all dependencies are listed in setup.py and requirements.txt

### Issue: ModuleNotFoundError: No module named 'langchain'

```
ImportError while loading conftest '...'.
__init__.py:9: in <module>
    from .supervisor import create_hotel_supervisor
supervisor.py:13: in <module>
    from langchain.prompts import ChatPromptTemplate
E   ModuleNotFoundError: No module named 'langchain'
```

**Solution:**

1. Install langchain and its dependencies:

```bash
pip install langchain langchain-core
```

2. Reinstall the package in development mode:

```bash
pip install -e .
```

3. If you're using a virtual environment, make sure it's activated:

```bash
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate
```

### Issue: Tests fail because of version conflicts

```
ImportError: cannot import name 'SomeClass' from 'some_module'
```

**Solution:**

1. Check the version of the dependency:

```bash
pip show some_module
```

2. Install the correct version:

```bash
pip install some_module==X.Y.Z
```

## Running Specific Tests

### Issue: Need to run only specific tests

**Solution:**

1. Run a specific test file:

```bash
python run_tests.py --test tests/rag/test_processor.py
```

2. Run tests for a specific module:

```bash
python run_tests.py --module rag
```

3. Run a specific test function:

```bash
python -m pytest tests/rag/test_processor.py::TestTextProcessor::test_chunk_text
```

## Getting Help

If you're still having issues, please:

1. Check the test logs for more information
2. Look at the test code to understand what it's testing
3. Check the implementation code to see if it matches the test expectations
4. Reach out to the development team for assistance