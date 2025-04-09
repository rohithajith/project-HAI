"""
Vector store for the RAG module.

This module provides an enhanced vector store implementation using FAISS for efficient
similarity search of document embeddings, with support for multiple indexes,
metadata filtering, and advanced search capabilities.
"""

import os
import pickle
import logging
import numpy as np
import json
import time
from typing import List, Dict, Any, Optional, Tuple, Union, Set
from pydantic import BaseModel, Field
from datetime import datetime

logger = logging.getLogger(__name__)

class Document(BaseModel):
    """Schema for documents in the vector store."""
    id: str
    content: str
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None

class VectorStoreStats(BaseModel):
    """Statistics for the vector store."""
    document_count: int
    embedding_dimension: int
    index_type: str
    categories: Dict[str, int]
    last_updated: str
    index_size_bytes: int
    metadata_fields: List[str]

class VectorStore:
    """Enhanced vector store for document embeddings using FAISS."""
    
    def __init__(self, embedding_dim: int = 768, index_path: Optional[str] = None,
                 index_type: str = "flat", use_gpu: bool = False):
        """Initialize the vector store with configurable index type.
        
        Args:
            embedding_dim: Dimension of the embeddings
            index_path: Path to save/load the FAISS index
            index_type: Type of FAISS index ("flat", "ivf", "hnsw")
            use_gpu: Whether to use GPU for FAISS
        """
        try:
            import faiss
        except ImportError:
            logger.error("FAISS is not installed. Please install it with: pip install faiss-cpu or faiss-gpu")
            raise ImportError("FAISS is required for the vector store")
            
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.use_gpu = use_gpu
        self.index_path = index_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data/vector_db/hotel_info.faiss"
        )
        self.docs_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data/vector_db/hotel_info_docs.pkl"
        )
        self.stats_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data/vector_db/hotel_info_stats.json"
        )
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        # Initialize or load index
        self.faiss = faiss
        self.index = None
        self.documents = {}
        self._load_or_create_index()
        
        # Initialize document ID mapping
        self._update_id_mapping()
        
        logger.info(f"Vector store initialized with dimension {embedding_dim} using {index_type} index")
    
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
            # Create new index based on index type
            logger.info(f"Creating new FAISS {self.index_type} index")
            
            if self.index_type == "flat":
                self.index = self.faiss.IndexFlatL2(self.embedding_dim)
            elif self.index_type == "ivf":
                # IVF index requires training, so we start with a flat index
                # and will train it when we have enough data
                quantizer = self.faiss.IndexFlatL2(self.embedding_dim)
                self.index = self.faiss.IndexIVFFlat(quantizer, self.embedding_dim, 100)
                self.index.nprobe = 10  # Number of clusters to search
            elif self.index_type == "hnsw":
                self.index = self.faiss.IndexHNSWFlat(self.embedding_dim, 32)  # 32 neighbors
            else:
                logger.warning(f"Unknown index type {self.index_type}, falling back to flat index")
                self.index = self.faiss.IndexFlatL2(self.embedding_dim)
            
            self.documents = {}
        
        # Move to GPU if requested and available
        if self.use_gpu:
            try:
                res = self.faiss.StandardGpuResources()
                self.index = self.faiss.index_cpu_to_gpu(res, 0, self.index)
                logger.info("Moved FAISS index to GPU")
            except Exception as e:
                logger.warning(f"Failed to move index to GPU: {e}")
    
    def _update_id_mapping(self):
        """Update the mapping from index positions to document IDs."""
        self.id_to_index = {doc_id: i for i, doc_id in enumerate(self.documents.keys())}
        self.index_to_id = {i: doc_id for doc_id, i in self.id_to_index.items()}
    
    def add_documents(self, documents: List[Document], update_if_exists: bool = True):
        """Add documents to the vector store with duplicate handling.
        
        Args:
            documents: List of documents to add
            update_if_exists: Whether to update existing documents
        """
        if not documents:
            return
        
        # Filter documents with embeddings
        docs_with_embeddings = [doc for doc in documents if doc.embedding is not None]
        
        if not docs_with_embeddings:
            logger.warning("No documents with embeddings to add")
            return
        
        # Handle existing documents
        new_docs = []
        updated_docs = []
        
        for doc in docs_with_embeddings:
            if doc.id in self.documents:
                if update_if_exists:
                    # Update existing document
                    updated_docs.append(doc)
                    self.documents[doc.id] = doc
            else:
                # New document
                new_docs.append(doc)
                self.documents[doc.id] = doc
        
        # Add new documents to index
        if new_docs:
            embeddings = np.array([doc.embedding for doc in new_docs], dtype=np.float32)
            
            # Train IVF index if needed
            if self.index_type == "ivf" and not self.index.is_trained and len(new_docs) >= 100:
                logger.info("Training IVF index")
                self.index.train(embeddings)
            
            # Add to index
            self.index.add(embeddings)
            
            logger.info(f"Added {len(new_docs)} new documents to vector store")
        
        # Update existing documents in index
        if updated_docs and update_if_exists:
            for doc in updated_docs:
                # Get index position
                if doc.id in self.id_to_index:
                    idx = self.id_to_index[doc.id]
                    
                    # Update embedding at index position
                    embedding = np.array([doc.embedding], dtype=np.float32)
                    
                    # For flat index, we need to remove and re-add
                    # For other index types, we might need different approaches
                    # This is a simplification and might not work for all index types
                    logger.warning(f"Updating embeddings in-place is not fully supported for all index types")
            
            logger.info(f"Updated {len(updated_docs)} existing documents in vector store")
        
        # Update ID mapping
        self._update_id_mapping()
        
        # Save index and documents
        self._save()
    
    def search(self, query_embedding: List[float], k: int = 5,
              filter_metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """Search for similar documents with optional metadata filtering.
        
        Args:
            query_embedding: Embedding of the query
            k: Number of results to return
            filter_metadata: Metadata filters to apply
            
        Returns:
            List of similar documents
        """
        if self.index.ntotal == 0:
            logger.warning("Vector store is empty")
            return []
        
        # Convert to numpy array
        query_np = np.array([query_embedding], dtype=np.float32)
        
        # Search
        distances, indices = self.index.search(query_np, min(k * 2, self.index.ntotal))
        
        # Get documents
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:  # FAISS returns -1 for empty slots
                doc_id = self.index_to_id.get(idx, list(self.documents.keys())[idx])
                doc = self.documents[doc_id]
                
                # Apply metadata filters
                if filter_metadata and not self._matches_filter(doc.metadata, filter_metadata):
                    continue
                
                # Add distance to metadata
                doc_with_score = Document(
                    id=doc.id,
                    content=doc.content,
                    metadata={**doc.metadata, "score": float(distances[0][i])},
                    embedding=doc.embedding
                )
                results.append(doc_with_score)
                
                # Stop if we have enough results
                if len(results) >= k:
                    break
        
        return results
    
    def _matches_filter(self, metadata: Dict[str, Any], filter_metadata: Dict[str, Any]) -> bool:
        """Check if metadata matches filter criteria.
        
        Args:
            metadata: Document metadata
            filter_metadata: Filter criteria
            
        Returns:
            True if metadata matches filter
        """
        for key, value in filter_metadata.items():
            if key not in metadata:
                return False
                
            if isinstance(value, list):
                # List of acceptable values
                if metadata[key] not in value:
                    return False
            elif isinstance(value, dict):
                # Range filter
                if "min" in value and metadata[key] < value["min"]:
                    return False
                if "max" in value and metadata[key] > value["max"]:
                    return False
            else:
                # Exact match
                if metadata[key] != value:
                    return False
        
        return True
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document or None if not found
        """
        return self.documents.get(doc_id)
    
    def get_all_documents(self) -> List[Document]:
        """Get all documents in the vector store.
        
        Returns:
            List of all documents
        """
        return list(self.documents.values())
    
    def get_document_count(self) -> int:
        """Get the number of documents in the vector store.
        
        Returns:
            Number of documents
        """
        return len(self.documents)
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the vector store.
        
        Note: This doesn't actually remove the embedding from the FAISS index,
        but marks it as deleted in our document store. A full rebuild is needed
        to actually remove it from the index.
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if document was deleted
        """
        if doc_id in self.documents:
            del self.documents[doc_id]
            self._update_id_mapping()
            self._save()
            logger.info(f"Deleted document {doc_id} from vector store")
            return True
        return False
    
    def get_documents_by_metadata(self, metadata_filter: Dict[str, Any], limit: int = 100) -> List[Document]:
        """Get documents by metadata filter.
        
        Args:
            metadata_filter: Metadata filter criteria
            limit: Maximum number of documents to return
            
        Returns:
            List of matching documents
        """
        results = []
        for doc in self.documents.values():
            if self._matches_filter(doc.metadata, metadata_filter):
                results.append(doc)
                if len(results) >= limit:
                    break
        
        return results
    
    def _save(self):
        """Save the index and documents to disk."""
        # Move index to CPU if it's on GPU
        if self.use_gpu:
            try:
                cpu_index = self.faiss.index_gpu_to_cpu(self.index)
                self.faiss.write_index(cpu_index, self.index_path)
            except Exception as e:
                logger.warning(f"Failed to move index to CPU for saving: {e}")
                return
        else:
            self.faiss.write_index(self.index, self.index_path)
        
        with open(self.docs_path, 'wb') as f:
            pickle.dump(self.documents, f)
        
        # Save stats
        self._save_stats()
        
        logger.info(f"Saved vector store with {len(self.documents)} documents to {self.index_path}")
    
    def _save_stats(self):
        """Save vector store statistics."""
        # Count documents by category
        categories = {}
        for doc in self.documents.values():
            category = doc.metadata.get("category", "general")
            categories[category] = categories.get(category, 0) + 1
        
        # Get metadata fields
        metadata_fields = set()
        for doc in self.documents.values():
            metadata_fields.update(doc.metadata.keys())
        
        # Create stats
        stats = {
            "document_count": len(self.documents),
            "embedding_dimension": self.embedding_dim,
            "index_type": self.index_type,
            "categories": categories,
            "last_updated": datetime.now().isoformat(),
            "index_size_bytes": os.path.getsize(self.index_path) if os.path.exists(self.index_path) else 0,
            "metadata_fields": list(metadata_fields)
        }
        
        # Save stats
        with open(self.stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
    
    def get_stats(self) -> VectorStoreStats:
        """Get vector store statistics.
        
        Returns:
            Vector store statistics
        """
        # Count documents by category
        categories = {}
        for doc in self.documents.values():
            category = doc.metadata.get("category", "general")
            categories[category] = categories.get(category, 0) + 1
        
        # Get metadata fields
        metadata_fields = set()
        for doc in self.documents.values():
            metadata_fields.update(doc.metadata.keys())
        
        return VectorStoreStats(
            document_count=len(self.documents),
            embedding_dimension=self.embedding_dim,
            index_type=self.index_type,
            categories=categories,
            last_updated=datetime.now().isoformat(),
            index_size_bytes=os.path.getsize(self.index_path) if os.path.exists(self.index_path) else 0,
            metadata_fields=list(metadata_fields)
        )
    
    def clear(self):
        """Clear the vector store."""
        # Create new index based on index type
        if self.index_type == "flat":
            self.index = self.faiss.IndexFlatL2(self.embedding_dim)
        elif self.index_type == "ivf":
            quantizer = self.faiss.IndexFlatL2(self.embedding_dim)
            self.index = self.faiss.IndexIVFFlat(quantizer, self.embedding_dim, 100)
            self.index.nprobe = 10
        elif self.index_type == "hnsw":
            self.index = self.faiss.IndexHNSWFlat(self.embedding_dim, 32)
        else:
            self.index = self.faiss.IndexFlatL2(self.embedding_dim)
        
        # Move to GPU if requested
        if self.use_gpu:
            try:
                res = self.faiss.StandardGpuResources()
                self.index = self.faiss.index_cpu_to_gpu(res, 0, self.index)
            except Exception as e:
                logger.warning(f"Failed to move index to GPU: {e}")
        
        self.documents = {}
        self._update_id_mapping()
        self._save()
        logger.info("Vector store cleared")
    
    def rebuild_index(self):
        """Rebuild the index from scratch.
        
        This is useful after many document deletions or updates.
        """
        logger.info("Rebuilding vector store index")
        
        # Get all documents with embeddings
        docs_with_embeddings = [doc for doc in self.documents.values() if doc.embedding is not None]
        
        # Create new index
        if self.index_type == "flat":
            new_index = self.faiss.IndexFlatL2(self.embedding_dim)
        elif self.index_type == "ivf":
            quantizer = self.faiss.IndexFlatL2(self.embedding_dim)
            new_index = self.faiss.IndexIVFFlat(quantizer, self.embedding_dim, 100)
            new_index.nprobe = 10
        elif self.index_type == "hnsw":
            new_index = self.faiss.IndexHNSWFlat(self.embedding_dim, 32)
        else:
            new_index = self.faiss.IndexFlatL2(self.embedding_dim)
        
        # Add embeddings to new index
        if docs_with_embeddings:
            embeddings = np.array([doc.embedding for doc in docs_with_embeddings], dtype=np.float32)
            
            # Train IVF index if needed
            if self.index_type == "ivf" and len(docs_with_embeddings) >= 100:
                new_index.train(embeddings)
            
            # Add to index
            new_index.add(embeddings)
        
        # Replace old index
        self.index = new_index
        
        # Move to GPU if requested
        if self.use_gpu:
            try:
                res = self.faiss.StandardGpuResources()
                self.index = self.faiss.index_cpu_to_gpu(res, 0, self.index)
            except Exception as e:
                logger.warning(f"Failed to move index to GPU: {e}")
        
        # Update ID mapping
        self._update_id_mapping()
        
        # Save
        self._save()
        
        logger.info(f"Rebuilt index with {len(docs_with_embeddings)} documents")