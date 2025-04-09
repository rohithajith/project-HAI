"""
Embedding generator for the RAG module using a local model `finetuned_merged`.
"""

import os
import logging
import asyncio
import hashlib
import json
from typing import List, Union, Optional, Dict, Any
import torch
import numpy as np
from functools import lru_cache

try:
    from transformers import AutoTokenizer, AutoModel
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError("Install with: pip install transformers sentence-transformers")

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Generate embeddings for text using a local model."""
    
    def __init__(self, model_name: str = "finetuned_merged",
                 cache_dir: Optional[str] = None,
                 use_cache: bool = True,
                 cache_size: int = 10000):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.use_cache = use_cache
        self.cache_dir = cache_dir or os.path.join(os.getcwd(), "embedding_cache")
        self.model_path = os.path.abspath(self.model_name)

        if not os.path.exists(self.model_path):
            raise ValueError(f"Model path '{self.model_path}' does not exist.")
        
        os.makedirs(self.cache_dir, exist_ok=True)
        self.cache_file = os.path.join(self.cache_dir, f"{model_name.replace('/', '_')}_cache.json")
        self.embedding_cache = {}

        if self.use_cache and os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.embedding_cache = json.load(f)
                logger.info(f"Loaded {len(self.embedding_cache)} cached embeddings")
            except Exception as e:
                logger.warning(f"Failed to load embedding cache: {e}")

        # Try loading as SentenceTransformer
        try:
            self.model = SentenceTransformer(self.model_path).to(self.device)
            self.tokenizer = None
            self.use_sentence_transformers = True
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
        except Exception:
            # Fallback to transformers
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModel.from_pretrained(self.model_path).to(self.device)
            self.use_sentence_transformers = False
            self.embedding_dim = self.model.config.hidden_size

        self._generate_cached = lru_cache(maxsize=cache_size)(self._generate_text)

        logger.info(f"Loaded local model '{model_name}' ({'sentence-transformers' if self.use_sentence_transformers else 'transformers'}) on {self.device}")

    def generate(self, texts: Union[str, List[str]], batch_size: int = 8) -> List[List[float]]:
        if isinstance(texts, str):
            texts = [texts]

        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_embeddings = self._generate_batch(batch_texts)
            all_embeddings.extend(batch_embeddings)

        return all_embeddings

    def _generate_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        texts_to_embed = []
        indices_to_embed = []

        for i, text in enumerate(texts):
            if self.use_cache:
                embedding = self._get_from_cache(text)
                if embedding is not None:
                    embeddings.append(embedding)
                    continue
            texts_to_embed.append(text)
            indices_to_embed.append(i)

        new_embeddings = []
        if texts_to_embed:
            new_embeddings = self._generate_texts(texts_to_embed)
            if self.use_cache:
                for text, embedding in zip(texts_to_embed, new_embeddings):
                    self._add_to_cache(text, embedding)

        result = [None] * len(texts)
        for i, embedding in enumerate(embeddings):
            result[i] = embedding
        for i, embedding in zip(indices_to_embed, new_embeddings):
            result[i] = embedding

        return result

    def _generate_texts(self, texts: List[str]) -> List[List[float]]:
        if self.use_sentence_transformers:
            embeddings = self.model.encode(texts, convert_to_tensor=True)
            return embeddings.cpu().numpy().tolist()
        else:
            inputs = self.tokenizer(
                texts, padding=True, truncation=True, max_length=512, return_tensors="pt"
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)

            attention_mask = inputs["attention_mask"]
            token_embeddings = outputs.last_hidden_state
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
            sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
            return (sum_embeddings / sum_mask).cpu().numpy().tolist()

    def _generate_text(self, text: str) -> List[float]:
        return self._generate_texts([text])[0]

    def _get_from_cache(self, text: str) -> Optional[List[float]]:
        if not self.use_cache:
            return None
        text_hash = hashlib.md5(text.encode()).hexdigest()
        try:
            return self._generate_cached(text)
        except Exception:
            return self.embedding_cache.get(text_hash, None)

    def _add_to_cache(self, text: str, embedding: List[float]) -> None:
        if not self.use_cache:
            return
        text_hash = hashlib.md5(text.encode()).hexdigest()
        self.embedding_cache[text_hash] = embedding
        if len(self.embedding_cache) % 100 == 0:
            self._save_cache()

    def _save_cache(self) -> None:
        if not self.use_cache:
            return
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.embedding_cache, f)
            logger.info(f"Saved {len(self.embedding_cache)} embeddings to cache")
        except Exception as e:
            logger.warning(f"Failed to save embedding cache: {e}")

    async def generate_async(self, texts: Union[str, List[str]], batch_size: int = 8) -> List[List[float]]:
        if isinstance(texts, str):
            texts = [texts]
        tasks = []
        for i in range(0, len(texts), batch_size):
            task = asyncio.create_task(self._generate_batch_async(texts[i:i+batch_size]))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return [embed for batch in results for embed in batch]

    async def _generate_batch_async(self, texts: List[str]) -> List[List[float]]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._generate_batch, texts)

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "device": self.device,
            "cache_enabled": self.use_cache,
            "cache_size": len(self.embedding_cache) if self.use_cache else 0
        }