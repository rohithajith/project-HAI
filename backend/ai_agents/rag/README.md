# RAG Module for Hotel AI

This module implements Retrieval Augmented Generation (RAG) for the Hotel AI system, enhancing the AI's responses with hotel-specific information.

## Overview

The RAG module consists of several components:

1. **Vector Store**: Stores document embeddings for efficient similarity search
2. **Embedding Generator**: Generates embeddings for text using transformer models
3. **Text Processor**: Processes text for chunking, cleaning, and metadata extraction
4. **Retriever**: Retrieves relevant documents based on a query
5. **RAG Module**: Main module that ties everything together

## Usage

### Initializing the RAG Module

To initialize the RAG module with hotel information:

```bash
python init_rag.py [--hotel-info-dir PATH] [--clear]
```

Options:
- `--hotel-info-dir`: Directory containing hotel information files (default: `../data/hotel_info`)
- `--clear`: Clear existing vector store before ingestion

### Using the RAG Module in Agents

The RAG module is integrated with the agent system. To use it in an agent:

```python
from rag.rag_module import RAGModule, RAGQuery

# Initialize the RAG module
rag_module = RAGModule()

# Process a query
query = "What time is check-in?"
state = {"guest_name": "John Doe"}
rag_result = await rag_module.process_query(RAGQuery(query=query, context=state))

# Use the RAG context in your agent
context = rag_result.context
```

## Adding Hotel Information

To add hotel information, create text files in the `data/hotel_info` directory. Each file should contain information about a specific aspect of the hotel.

The system will automatically chunk the text, extract metadata, generate embeddings, and store them in the vector database.

## Requirements

See `requirements.txt` for the required dependencies.