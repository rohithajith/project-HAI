# Hotel AI System Tests

This directory contains tests for the Hotel AI system.

## Overview

The tests are organized by module:

- `rag/`: Tests for the Retrieval Augmented Generation (RAG) module
- `agents/`: Tests for the agent system
- `controllers/`: Tests for the controllers

## Running Tests

You can run the tests using the `run_tests.py` script:

```bash
# Run all tests
python run_tests.py

# Run tests for a specific module
python run_tests.py --module rag
python run_tests.py --module agents
python run_tests.py --module controllers

# Run a specific test file
python run_tests.py --test tests/rag/test_processor.py

# Run tests with verbose output
python run_tests.py --verbose

# Generate coverage report
python run_tests.py --coverage
```

## Test Coverage

The tests cover the following components:

### RAG Module

- **Vector Store**: Tests for document storage, retrieval, and persistence
- **Embedding Generator**: Tests for generating embeddings from text
- **Text Processor**: Tests for text chunking, cleaning, and metadata extraction
- **Retriever**: Tests for retrieving relevant documents based on queries
- **RAG Module**: Tests for the main RAG module that ties everything together

### Agents

- **Base Agent**: Tests for the base agent functionality
- **Hotel Info Agent**: Tests for the hotel information agent

### Controllers

- **Hotel Info Controller**: Tests for the hotel information controller

## Setup

### Quick Setup

The easiest way to set up the development environment is to use the provided setup script:

```bash
# Create a virtual environment and install all dependencies
python setup_dev_env.py --venv

# Use an existing Python environment
python setup_dev_env.py

# Upgrade existing packages
python setup_dev_env.py --upgrade
```

This script will:
1. Create a virtual environment (if requested)
2. Install the package in development mode
3. Install all required dependencies, including test dependencies
4. Install RAG module dependencies

### Manual Setup

If you prefer to set up the environment manually, you can follow these steps:

1. Create a virtual environment (optional):
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate
```

2. Install the package in development mode with test dependencies:
```bash
pip install -e ".[dev]"
```

3. Install RAG module dependencies:
```bash
pip install -r rag/requirements.txt
```

## Mocking

The tests use mocking to isolate components and avoid external dependencies:

- FAISS is mocked to avoid requiring the actual vector database
- Transformer models are mocked to avoid loading large models
- External APIs and services are mocked

## Adding New Tests

When adding new tests:

1. Create a new test file in the appropriate directory
2. Use the existing test files as templates
3. Follow the naming convention: `test_*.py`
4. Use pytest fixtures for common setup
5. Use mocking to isolate components
6. Run the tests to ensure they pass

## Continuous Integration

These tests are designed to be run in a CI/CD pipeline. They should be fast, reliable, and not depend on external services.