"""
Tests for the embedding generator module.
"""

import pytest
import torch
import numpy as np
from unittest.mock import patch, MagicMock
from rag.embeddings import EmbeddingGenerator

# Mock classes for transformers
class MockTokenizer:
    """Mock for the transformers tokenizer."""
    
    def __init__(self, *args, **kwargs):
        """Initialize the mock tokenizer."""
        pass
    
    def __call__(self, texts, padding=True, truncation=True, max_length=512, return_tensors="pt"):
        """Mock tokenization."""
        # Create a mock tensor with the right shape
        if isinstance(texts, str):
            texts = [texts]
        
        # Create mock input IDs and attention mask
        batch_size = len(texts)
        seq_length = min(max_length, max(len(text.split()) for text in texts) + 2)  # +2 for special tokens
        
        input_ids = torch.ones((batch_size, seq_length), dtype=torch.long)
        attention_mask = torch.ones((batch_size, seq_length), dtype=torch.long)
        
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask
        }

class MockModel:
    """Mock for the transformers model."""
    
    def __init__(self, *args, **kwargs):
        """Initialize the mock model."""
        pass
    
    def to(self, device):
        """Mock device placement."""
        return self
    
    def __call__(self, **inputs):
        """Mock forward pass."""
        # Create a mock output with the right shape
        batch_size = inputs["input_ids"].shape[0]
        seq_length = inputs["input_ids"].shape[1]
        hidden_size = 768
        
        last_hidden_state = torch.ones((batch_size, seq_length, hidden_size), dtype=torch.float)
        
        # Create a mock output object
        output = MagicMock()
        output.last_hidden_state = last_hidden_state
        
        return output

@pytest.fixture
def mock_transformers():
    """Fixture to mock transformers."""
    with patch('rag.embeddings.AutoTokenizer', return_value=MockTokenizer()), \
         patch('rag.embeddings.AutoModel', return_value=MockModel()):
        yield

@pytest.fixture
def embedding_generator(mock_transformers):
    """Fixture to create an embedding generator with mocked transformers."""
    return EmbeddingGenerator()

class TestEmbeddingGenerator:
    """Test cases for the EmbeddingGenerator class."""
    
    def test_init(self, embedding_generator):
        """Test initialization of the embedding generator."""
        assert embedding_generator.model_name == "BAAI/bge-small-en-v1.5"
        assert embedding_generator.device in ["cuda", "cpu"]
        assert embedding_generator.tokenizer is not None
        assert embedding_generator.model is not None
    
    def test_generate_single_text(self, embedding_generator):
        """Test generating embeddings for a single text."""
        text = "This is a test text."
        embeddings = embedding_generator.generate(text)
        
        # Check that we got a list of embeddings
        assert isinstance(embeddings, list)
        assert len(embeddings) == 1
        
        # Check the shape of the embeddings
        assert isinstance(embeddings[0], list)
        assert len(embeddings[0]) == 768  # Default embedding size
    
    def test_generate_multiple_texts(self, embedding_generator):
        """Test generating embeddings for multiple texts."""
        texts = ["This is the first text.", "This is the second text."]
        embeddings = embedding_generator.generate(texts)
        
        # Check that we got a list of embeddings
        assert isinstance(embeddings, list)
        assert len(embeddings) == 2
        
        # Check the shape of the embeddings
        assert isinstance(embeddings[0], list)
        assert isinstance(embeddings[1], list)
        assert len(embeddings[0]) == 768  # Default embedding size
        assert len(embeddings[1]) == 768  # Default embedding size
    
    def test_generate_batch_size(self, embedding_generator):
        """Test generating embeddings with different batch sizes."""
        texts = ["Text " + str(i) for i in range(10)]
        
        # Generate with default batch size
        embeddings1 = embedding_generator.generate(texts)
        
        # Generate with custom batch size
        embeddings2 = embedding_generator.generate(texts, batch_size=2)
        
        # Check that both methods produce the same number of embeddings
        assert len(embeddings1) == len(embeddings2) == 10
        
        # Check that all embeddings have the same shape
        for emb in embeddings1 + embeddings2:
            assert len(emb) == 768
    
    def test_generate_async(self, embedding_generator):
        """Test the async wrapper for generate method."""
        text = "This is a test text."
        embeddings = embedding_generator.generate_async(text)
        
        # Check that we got a list of embeddings
        assert isinstance(embeddings, list)
        assert len(embeddings) == 1
        
        # Check the shape of the embeddings
        assert isinstance(embeddings[0], list)
        assert len(embeddings[0]) == 768  # Default embedding size