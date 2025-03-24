"""
Embedding generator for the RAG module.

This module provides functionality to generate embeddings for text using
local transformer models.
"""

import os
import logging
from typing import List, Union, Optional
import torch
import numpy as np

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Generate embeddings for text using local models."""
    
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        """Initialize the embedding generator.
        
        Args:
            model_name: Name of the embedding model
        """
        try:
            from transformers import AutoTokenizer, AutoModel
        except ImportError:
            logger.error("Transformers is not installed. Please install it with: pip install transformers")
            raise ImportError("Transformers is required for the embedding generator")
            
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Loading embedding model {model_name} on {self.device}")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        
        logger.info("Embedding model loaded successfully")
    
    def generate(self, texts: Union[str, List[str]], batch_size: int = 8) -> List[List[float]]:
        """Generate embeddings for texts.
        
        Args:
            texts: Text or list of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            List of embeddings
        """
        # Convert single text to list
        if isinstance(texts, str):
            texts = [texts]
        
        # Process in batches
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_embeddings = self._generate_batch(batch_texts)
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
    
    def _generate_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        # Tokenize
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(self.device)
        
        # Generate embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Mean pooling
        attention_mask = inputs["attention_mask"]
        token_embeddings = outputs.last_hidden_state
        
        # Mask padding tokens
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        
        # Sum embeddings
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        
        # Normalize
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        embeddings = (sum_embeddings / sum_mask).cpu().numpy().tolist()
        
        return embeddings
    
    def generate_async(self, texts: Union[str, List[str]], batch_size: int = 8) -> List[List[float]]:
        """Async wrapper for generate method.
        
        This is a placeholder for future async implementation.
        Currently just calls the synchronous method.
        
        Args:
            texts: Text or list of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            List of embeddings
        """
        # In a real async implementation, this would use asyncio
        # For now, just call the synchronous method
        return self.generate(texts, batch_size)