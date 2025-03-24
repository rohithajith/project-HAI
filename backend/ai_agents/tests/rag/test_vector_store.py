"""
Tests for the vector store module.
"""

import os
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from rag.vector_store import VectorStore, Document

# Mock FAISS module
class MockFaiss:
    """Mock for the FAISS module."""
    
    @staticmethod
    def IndexFlatL2(dim):
        """Create a mock FAISS index."""
        return MockFaissIndex(dim)
    
    @staticmethod
    def read_index(path):
        """Read a mock FAISS index."""
        return MockFaissIndex(768)
    
    @staticmethod
    def write_index(index, path):
        """Write a mock FAISS index."""
        pass

class MockFaissIndex:
    """Mock for a FAISS index."""
    
    def __init__(self, dim):
        """Initialize the mock index."""
        self.dim = dim
        self.vectors = []
        self.ntotal = 0
    
    def add(self, vectors):
        """Add vectors to the mock index."""
        self.vectors.extend(vectors)
        self.ntotal = len(self.vectors)
    
    def search(self, query, k):
        """Search the mock index."""
        # Return mock distances and indices
        distances = np.array([[0.1, 0.2, 0.3, 0.4, 0.5][:min(k, self.ntotal)]])
        indices = np.array([[i for i in range(min(k, self.ntotal))]])
        return distances, indices

@pytest.fixture
def mock_faiss():
    """Fixture to mock FAISS."""
    with patch('rag.vector_store.faiss', MockFaiss()) as mock:
        yield mock

@pytest.fixture
def temp_dir(tmpdir):
    """Fixture to create a temporary directory."""
    return tmpdir.mkdir("vector_store_test")

@pytest.fixture
def vector_store(mock_faiss, temp_dir):
    """Fixture to create a vector store with mocked FAISS."""
    index_path = os.path.join(temp_dir, "test.faiss")
    docs_path = os.path.join(temp_dir, "test_docs.pkl")
    
    with patch('rag.vector_store.os.path.exists', return_value=False):
        store = VectorStore(embedding_dim=768, index_path=index_path)
        store.docs_path = docs_path
        return store

class TestVectorStore:
    """Test cases for the VectorStore class."""
    
    def test_init(self, vector_store):
        """Test initialization of the vector store."""
        assert vector_store.embedding_dim == 768
        assert vector_store.index is not None
        assert vector_store.documents == {}
    
    def test_add_documents(self, vector_store):
        """Test adding documents to the vector store."""
        # Create test documents
        docs = [
            Document(
                id="test1",
                content="This is a test document",
                metadata={"category": "test"},
                embedding=[0.1] * 768
            ),
            Document(
                id="test2",
                content="This is another test document",
                metadata={"category": "test"},
                embedding=[0.2] * 768
            )
        ]
        
        # Add documents
        vector_store.add_documents(docs)
        
        # Check that documents were added
        assert len(vector_store.documents) == 2
        assert "test1" in vector_store.documents
        assert "test2" in vector_store.documents
    
    def test_add_documents_no_embeddings(self, vector_store):
        """Test adding documents without embeddings."""
        # Create test documents without embeddings
        docs = [
            Document(
                id="test1",
                content="This is a test document",
                metadata={"category": "test"}
            ),
            Document(
                id="test2",
                content="This is another test document",
                metadata={"category": "test"}
            )
        ]
        
        # Add documents
        vector_store.add_documents(docs)
        
        # Check that no documents were added
        assert len(vector_store.documents) == 0
    
    def test_search(self, vector_store):
        """Test searching for documents."""
        # Add test documents
        docs = [
            Document(
                id="test1",
                content="This is a test document",
                metadata={"category": "test"},
                embedding=[0.1] * 768
            ),
            Document(
                id="test2",
                content="This is another test document",
                metadata={"category": "test"},
                embedding=[0.2] * 768
            )
        ]
        vector_store.add_documents(docs)
        
        # Search for documents
        query_embedding = [0.3] * 768
        results = vector_store.search(query_embedding, k=2)
        
        # Check results
        assert len(results) == 2
        assert results[0].id in ["test1", "test2"]
        assert results[1].id in ["test1", "test2"]
        assert "score" in results[0].metadata
    
    def test_search_empty(self, vector_store):
        """Test searching an empty vector store."""
        query_embedding = [0.3] * 768
        results = vector_store.search(query_embedding, k=2)
        
        # Check results
        assert len(results) == 0
    
    def test_clear(self, vector_store):
        """Test clearing the vector store."""
        # Add test documents
        docs = [
            Document(
                id="test1",
                content="This is a test document",
                metadata={"category": "test"},
                embedding=[0.1] * 768
            )
        ]
        vector_store.add_documents(docs)
        
        # Clear the vector store
        vector_store.clear()
        
        # Check that the vector store is empty
        assert len(vector_store.documents) == 0
        assert vector_store.index.ntotal == 0