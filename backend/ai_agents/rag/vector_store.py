"""
Vector store for the RAG module.

This module provides a vector store implementation using FAISS for efficient
similarity search of document embeddings.
"""

import os
import pickle
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class Document(BaseModel):
    """Schema for documents in the vector store."""
    id: str
    content: str
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None

class VectorStore:
    """Vector store for document embeddings using FAISS."""
    
    def __init__(self, embedding_dim: int = 768, index_path: Optional[str] = None):
        """Initialize the vector store.
        
        Args:
            embedding_dim: Dimension of the embeddings
            index_path: Path to save/load the FAISS index
        """
        try:
            import faiss
        except ImportError:
            logger.error("FAISS is not installed. Please install it with: pip install faiss-cpu or faiss-gpu")
            raise ImportError("FAISS is required for the vector store")
            
        self.embedding_dim = embedding_dim
        self.index_path = index_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "data/vector_db/hotel_info.faiss"
        )
        self.docs_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "data/vector_db/hotel_info_docs.pkl"
        )
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        # Initialize or load index
        self.faiss = faiss
        self.index = None
        self.documents = {}
        self._load_or_create_index()
        
        logger.info(f"Vector store initialized with dimension {embedding_dim}")
    
    def _load_or_create_index(self):
        """Load existing index or create a new one."""
        if os.path.exists(self.index_path) and os.path.exists(self.docs_path):
            # Load existing index and documents
            logger.info(f"Loading existing index from {self.index_path}")
            self.index = self.faiss.read_index(self.index_path)
            
            with open(self.docs_path, 'rb') as f:
                self.documents = pickle.load(f)
            
            logger.info(f"Loaded {len(self.documents)} documents")
        else:
            # Create new index
            logger.info("Creating new FAISS index")
            self.index = self.faiss.IndexFlatL2(self.embedding_dim)
            self.documents = {}
    
    def add_documents(self, documents: List[Document]):
        """Add documents to the vector store.
        
        Args:
            documents: List of documents to add
        """
        if not documents:
            return
        
        # Filter documents with embeddings
        docs_with_embeddings = [doc for doc in documents if doc.embedding is not None]
        
        if not docs_with_embeddings:
            logger.warning("No documents with embeddings to add")
            return
        
        # Extract embeddings
        embeddings = np.array([doc.embedding for doc in docs_with_embeddings], dtype=np.float32)
        
        # Add to index
        self.index.add(embeddings)
        
        # Store documents
        for i, doc in enumerate(docs_with_embeddings):
            self.documents[doc.id] = doc
        
        # Save index and documents
        self._save()
        
        logger.info(f"Added {len(docs_with_embeddings)} documents to vector store")
    
    def search(self, query_embedding: List[float], k: int = 5) -> List[Document]:
        """Search for similar documents.
        
        Args:
            query_embedding: Embedding of the query
            k: Number of results to return
            
        Returns:
            List of similar documents
        """
        if self.index.ntotal == 0:
            logger.warning("Vector store is empty")
            return []
        
        # Convert to numpy array
        query_np = np.array([query_embedding], dtype=np.float32)
        
        # Search
        distances, indices = self.index.search(query_np, k)
        
        # Get documents
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:  # FAISS returns -1 for empty slots
                doc_id = list(self.documents.keys())[idx]
                doc = self.documents[doc_id]
                
                # Add distance to metadata
                doc_with_score = Document(
                    id=doc.id,
                    content=doc.content,
                    metadata={**doc.metadata, "score": float(distances[0][i])},
                    embedding=doc.embedding
                )
                results.append(doc_with_score)
        
        return results
    
    def _save(self):
        """Save the index and documents to disk."""
        self.faiss.write_index(self.index, self.index_path)
        
        with open(self.docs_path, 'wb') as f:
            pickle.dump(self.documents, f)
        
        logger.info(f"Saved vector store to {self.index_path}")
    
    def clear(self):
        """Clear the vector store."""
        self.index = self.faiss.IndexFlatL2(self.embedding_dim)
        self.documents = {}
        self._save()
        logger.info("Vector store cleared")