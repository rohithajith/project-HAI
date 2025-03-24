"""
Text processor for the RAG module.

This module provides utilities for processing text, including chunking,
cleaning, and metadata extraction.
"""

import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class TextProcessor:
    """Process text for RAG."""
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in words
            overlap: Overlap between chunks in words
            
        Returns:
            List of text chunks
        """
        # Split into words
        words = text.split()
        
        # Create chunks
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + min(chunk_size, len(words) - i)])
            chunks.append(chunk)
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text for processing.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters (but keep important punctuation)
        text = re.sub(r'[^\w\s.,?!;:()\-\'"]', ' ', text)
        
        return text
    
    @staticmethod
    def extract_metadata(text: str) -> Dict[str, Any]:
        """Extract metadata from text.
        
        Args:
            text: Text to extract metadata from
            
        Returns:
            Metadata dictionary
        """
        metadata = {}
        
        # Extract potential categories based on keywords
        if re.search(r'\b(room|suite|accommodation|bed|pillow|towel)\b', text, re.IGNORECASE):
            metadata["category"] = "rooms"
        elif re.search(r'\b(restaurant|dining|breakfast|lunch|dinner|meal|food|menu|cuisine)\b', text, re.IGNORECASE):
            metadata["category"] = "dining"
        elif re.search(r'\b(spa|massage|wellness|treatment|therapy|relax|facial)\b', text, re.IGNORECASE):
            metadata["category"] = "spa"
        elif re.search(r'\b(pool|gym|fitness|exercise|workout|swim|sauna)\b', text, re.IGNORECASE):
            metadata["category"] = "facilities"
        elif re.search(r'\b(check-in|check-out|booking|reservation|cancel|policy)\b', text, re.IGNORECASE):
            metadata["category"] = "policies"
        elif re.search(r'\b(wifi|internet|connection|password|network)\b', text, re.IGNORECASE):
            metadata["category"] = "amenities"
        elif re.search(r'\b(event|conference|meeting|wedding|banquet|hall)\b', text, re.IGNORECASE):
            metadata["category"] = "events"
        elif re.search(r'\b(transport|shuttle|taxi|airport|parking|car)\b', text, re.IGNORECASE):
            metadata["category"] = "transportation"
        else:
            metadata["category"] = "general"
        
        # Extract potential sentiment
        positive_words = r'\b(excellent|great|good|best|amazing|wonderful|fantastic|perfect|enjoy|love)\b'
        negative_words = r'\b(bad|poor|terrible|worst|awful|horrible|disappointing|issue|problem|complaint)\b'
        
        if re.search(positive_words, text, re.IGNORECASE):
            metadata["sentiment"] = "positive"
        elif re.search(negative_words, text, re.IGNORECASE):
            metadata["sentiment"] = "negative"
        else:
            metadata["sentiment"] = "neutral"
        
        return metadata
    
    @staticmethod
    def preprocess_query(query: str) -> str:
        """Preprocess a query for retrieval.
        
        Args:
            query: Query to preprocess
            
        Returns:
            Preprocessed query
        """
        # Clean the query
        query = TextProcessor.clean_text(query)
        
        # Remove question words and common prefixes
        query = re.sub(r'^(what|where|when|who|how|can you|could you|please|tell me about|i want to know about)\s+', '', query, flags=re.IGNORECASE)
        
        # Remove trailing punctuation
        query = query.rstrip('?!.,;:')
        
        return query