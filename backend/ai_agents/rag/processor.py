"""
Text processor for the RAG module.

This module provides advanced utilities for processing text, including chunking,
cleaning, metadata extraction, and query expansion.
"""

import re
import logging
import nltk
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import Counter
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class TextProcessor:
    """Advanced text processing for RAG."""
    
    # Initialize NLP components
    try:
        # Download NLTK resources if not already downloaded
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
            
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
            
        # Load local finetuned model
        try:
            # Import and load the local finetuned model
            from backend.ai_agents.models import load_finetuned_model
            nlp = load_finetuned_model("finetuned_merged")
            SPACY_AVAILABLE = True
        except Exception as e:
            SPACY_AVAILABLE = False
            logger.warning(f"Local finetuned model not available: {e}. Some advanced features will be disabled.")
    except Exception as e:
        logger.warning(f"Error initializing NLP components: {e}")
        SPACY_AVAILABLE = False
    
    # Load stopwords
    try:
        from nltk.corpus import stopwords
        STOPWORDS = set(stopwords.words('english'))
    except:
        STOPWORDS = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
                         "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself',
                         'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her',
                         'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them',
                         'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom',
                         'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was',
                         'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do',
                         'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or',
                         'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with',
                         'about', 'against', 'between', 'into', 'through', 'during', 'before',
                         'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
                         'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
                         'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both',
                         'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
                         'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very'])
    
    # Hotel-specific categories and keywords
    HOTEL_CATEGORIES = {
        "rooms": [
            "room", "suite", "accommodation", "bed", "pillow", "towel", "bathroom",
            "shower", "bathtub", "toilet", "amenity", "tv", "television", "minibar"
        ],
        "dining": [
            "restaurant", "dining", "breakfast", "lunch", "dinner", "meal", "food",
            "menu", "cuisine", "chef", "reservation", "table", "buffet", "cafe",
            "bar", "drink", "beverage", "wine", "cocktail"
        ],
        "spa": [
            "spa", "massage", "wellness", "treatment", "therapy", "relax", "facial",
            "manicure", "pedicure", "sauna", "steam", "jacuzzi", "hot tub"
        ],
        "facilities": [
            "pool", "gym", "fitness", "exercise", "workout", "swim", "sauna",
            "business center", "conference", "meeting room", "lobby", "elevator",
            "lift", "garden", "terrace", "balcony"
        ],
        "policies": [
            "check-in", "check-out", "booking", "reservation", "cancel", "policy",
            "pet", "smoking", "payment", "deposit", "refund", "guarantee", "id",
            "identification", "passport", "credit card"
        ],
        "amenities": [
            "wifi", "internet", "connection", "password", "network", "free",
            "complimentary", "toiletry", "hairdryer", "iron", "safe", "voltage",
            "adapter", "charger", "phone", "laundry", "dry cleaning"
        ],
        "events": [
            "event", "conference", "meeting", "wedding", "banquet", "hall",
            "celebration", "party", "ceremony", "reception", "catering"
        ],
        "transportation": [
            "transport", "shuttle", "taxi", "airport", "parking", "car", "rental",
            "valet", "bus", "train", "subway", "metro", "station", "directions"
        ],
        "activities": [
            "activity", "tour", "excursion", "sightseeing", "guide", "ticket",
            "attraction", "museum", "theater", "show", "concert", "beach", "golf",
            "tennis", "sport", "hiking", "biking"
        ],
        "services": [
            "service", "concierge", "reception", "front desk", "housekeeping",
            "room service", "wake-up call", "luggage", "baggage", "storage",
            "security", "medical", "doctor", "emergency"
        ]
    }
    
    @classmethod
    def chunk_text(cls, text: str, chunk_size: int = 300, overlap: int = 50,
                  chunk_by: str = "word", respect_paragraphs: bool = True) -> List[str]:
        """Split text into overlapping chunks with advanced options.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in words or characters
            overlap: Overlap between chunks in words or characters
            chunk_by: Chunking method ("word", "char", "sentence", "paragraph")
            respect_paragraphs: Try to keep paragraphs together
            
        Returns:
            List of text chunks
        """
        # Clean text
        text = cls.clean_text(text)
        
        # Handle different chunking methods
        if chunk_by == "word":
            # Split into words
            words = text.split()
            
            # Create chunks
            chunks = []
            for i in range(0, len(words), chunk_size - overlap):
                chunk = " ".join(words[i:i + min(chunk_size, len(words) - i)])
                chunks.append(chunk)
                
        elif chunk_by == "char":
            # Create chunks by character
            chunks = []
            for i in range(0, len(text), chunk_size - overlap):
                chunk = text[i:i + min(chunk_size, len(text) - i)]
                chunks.append(chunk)
                
        elif chunk_by == "sentence":
            # Split into sentences
            try:
                sentences = nltk.sent_tokenize(text)
                
                # Create chunks of sentences
                chunks = []
                current_chunk = []
                current_size = 0
                
                for sentence in sentences:
                    sentence_size = len(sentence.split())
                    
                    if current_size + sentence_size <= chunk_size:
                        current_chunk.append(sentence)
                        current_size += sentence_size
                    else:
                        # Add current chunk to chunks
                        if current_chunk:
                            chunks.append(" ".join(current_chunk))
                        
                        # Start new chunk with overlap
                        if overlap > 0 and current_chunk:
                            # Calculate overlap in sentences
                            overlap_size = 0
                            overlap_chunk = []
                            
                            for s in reversed(current_chunk):
                                s_size = len(s.split())
                                if overlap_size + s_size <= overlap:
                                    overlap_chunk.insert(0, s)
                                    overlap_size += s_size
                                else:
                                    break
                            
                            current_chunk = overlap_chunk
                            current_size = overlap_size
                        else:
                            current_chunk = []
                            current_size = 0
                        
                        current_chunk.append(sentence)
                        current_size += sentence_size
                
                # Add the last chunk
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
            except Exception as e:
                logger.warning(f"Error chunking by sentence: {e}. Falling back to word chunking.")
                return cls.chunk_text(text, chunk_size, overlap, "word", respect_paragraphs)
                
        elif chunk_by == "paragraph":
            # Split into paragraphs
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            
            # Create chunks of paragraphs
            chunks = []
            current_chunk = []
            current_size = 0
            
            for paragraph in paragraphs:
                paragraph_size = len(paragraph.split())
                
                if current_size + paragraph_size <= chunk_size:
                    current_chunk.append(paragraph)
                    current_size += paragraph_size
                else:
                    # Add current chunk to chunks
                    if current_chunk:
                        chunks.append("\n\n".join(current_chunk))
                    
                    # Start new chunk
                    current_chunk = [paragraph]
                    current_size = paragraph_size
            
            # Add the last chunk
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
        else:
            # Default to word chunking
            return cls.chunk_text(text, chunk_size, overlap, "word", respect_paragraphs)
        
        logger.info(f"Split text into {len(chunks)} chunks using {chunk_by} chunking")
        return chunks
    
    @classmethod
    def clean_text(cls, text: str, aggressive: bool = False) -> str:
        """Clean text for processing with configurable aggressiveness.
        
        Args:
            text: Text to clean
            aggressive: Whether to use aggressive cleaning
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
            
        # Basic cleaning
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        if aggressive:
            # Aggressive cleaning
            # Convert to lowercase
            text = text.lower()
            
            # Remove special characters (but keep important punctuation)
            text = re.sub(r'[^\w\s.,?!;:()\-]', ' ', text)
            
            # Remove stopwords
            words = text.split()
            words = [w for w in words if w.lower() not in cls.STOPWORDS]
            text = " ".join(words)
        else:
            # Standard cleaning
            # Remove special characters (but keep important punctuation)
            text = re.sub(r'[^\w\s.,?!;:()\-\'"]', ' ', text)
        
        # Final whitespace cleanup
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @classmethod
    def extract_metadata(cls, text: str) -> Dict[str, Any]:
        """Extract rich metadata from text using NLP techniques.
        
        Args:
            text: Text to extract metadata from
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "length": len(text),
            "word_count": len(text.split())
        }
        
        # Extract categories based on keywords
        categories = []
        category_scores = {}
        
        for category, keywords in cls.HOTEL_CATEGORIES.items():
            score = 0
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, text, re.IGNORECASE)
                score += len(matches)
            
            if score > 0:
                categories.append(category)
                category_scores[category] = score
        
        # Sort categories by score
        if categories:
            primary_category = max(category_scores.items(), key=lambda x: x[1])[0]
            metadata["category"] = primary_category
            metadata["all_categories"] = categories
            metadata["category_scores"] = category_scores
        else:
            metadata["category"] = "general"
        
        # Extract sentiment
        positive_words = r'\b(excellent|great|good|best|amazing|wonderful|fantastic|perfect|enjoy|love|clean|comfortable|friendly|helpful|recommend|luxury|spacious|convenient|beautiful|delicious)\b'
        negative_words = r'\b(bad|poor|terrible|worst|awful|horrible|disappointing|issue|problem|complaint|dirty|uncomfortable|rude|unhelpful|avoid|small|inconvenient|expensive|noisy|broken)\b'
        
        positive_count = len(re.findall(positive_words, text, re.IGNORECASE))
        negative_count = len(re.findall(negative_words, text, re.IGNORECASE))
        
        if positive_count > negative_count:
            metadata["sentiment"] = "positive"
            metadata["sentiment_score"] = min(1.0, positive_count / (positive_count + negative_count + 1))
        elif negative_count > positive_count:
            metadata["sentiment"] = "negative"
            metadata["sentiment_score"] = -min(1.0, negative_count / (positive_count + negative_count + 1))
        else:
            metadata["sentiment"] = "neutral"
            metadata["sentiment_score"] = 0.0
        
        # Extract entities if spaCy is available
        if cls.SPACY_AVAILABLE:
            try:
                doc = cls.nlp(text[:5000])  # Limit to 5000 chars for performance
                
                entities = {}
                for ent in doc.ents:
                    if ent.label_ not in entities:
                        entities[ent.label_] = []
                    if ent.text not in entities[ent.label_]:
                        entities[ent.label_].append(ent.text)
                
                if entities:
                    metadata["entities"] = entities
                    
                # Extract key phrases (noun chunks)
                key_phrases = [chunk.text for chunk in doc.noun_chunks]
                if key_phrases:
                    metadata["key_phrases"] = key_phrases[:10]  # Top 10 phrases
            except Exception as e:
                logger.warning(f"Error extracting entities with spaCy: {e}")
        
        # Extract dates and times
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or DD/MM/YYYY
            r'\b\d{1,2}:\d{2}\s*(?:AM|PM)?\b',     # HH:MM AM/PM
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}(?:st|nd|rd|th)?,? \d{2,4}\b'  # Month Day, Year
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        
        if dates:
            metadata["dates"] = dates
        
        return metadata
    
    @classmethod
    def preprocess_query(cls, query: str, expand: bool = True) -> str:
        """Preprocess and optionally expand a query for retrieval.
        
        Args:
            query: Query to preprocess
            expand: Whether to expand the query with synonyms
            
        Returns:
            Preprocessed query
        """
        if not query:
            return ""
            
        # Clean the query
        query = cls.clean_text(query)
        
        # Remove question words and common prefixes
        query = re.sub(r'^(what|where|when|who|how|can you|could you|please|tell me about|i want to know about)\s+', '', query, flags=re.IGNORECASE)
        
        # Remove trailing punctuation
        query = query.rstrip('?!.,;:')
        
        return query
    
    @classmethod
    def expand_query(cls, query: str) -> List[str]:
        """Expand a query with synonyms and related terms.
        
        Args:
            query: Query to expand
            
        Returns:
            List of expanded queries
        """
        expanded_queries = [query]
        
        # Simple rule-based expansion
        lower_query = query.lower()
        
        # Hotel-specific expansions
        expansions = {
            "room": ["accommodation", "suite", "lodging"],
            "breakfast": ["morning meal", "breakfast buffet", "continental breakfast"],
            "wifi": ["internet", "wireless", "connection"],
            "check-in": ["check in", "checkin", "arrival"],
            "check-out": ["check out", "checkout", "departure"],
            "restaurant": ["dining", "eatery", "cafe"],
            "gym": ["fitness center", "workout", "exercise"],
            "pool": ["swimming pool", "swim"],
            "spa": ["wellness", "massage", "treatment"],
            "bathroom": ["restroom", "toilet", "shower"],
            "price": ["cost", "rate", "fee"],
            "reservation": ["booking", "reserve"],
            "parking": ["garage", "valet", "car park"]
        }
        
        # Add expansions
        for term, synonyms in expansions.items():
            if term in lower_query:
                for synonym in synonyms:
                    expanded_query = query.replace(term, synonym)
                    expanded_queries.append(expanded_query)
        
        return expanded_queries
    
    @classmethod
    def extract_keywords(cls, text: str, top_n: int = 10) -> List[str]:
        """Extract keywords from text.
        
        Args:
            text: Text to extract keywords from
            top_n: Number of top keywords to return
            
        Returns:
            List of keywords
        """
        # Tokenize and clean
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Remove stopwords
        words = [w for w in words if w not in cls.STOPWORDS and len(w) > 2]
        
        # Count word frequencies
        word_counts = Counter(words)
        
        # Get top keywords
        keywords = [word for word, count in word_counts.most_common(top_n)]
        
        return keywords
    
    @classmethod
    def generate_query_variations(cls, query: str) -> List[str]:
        """Generate variations of a query for better retrieval.
        
        Args:
            query: Original query
            
        Returns:
            List of query variations
        """
        variations = [query]
        
        # Clean query
        clean_query = cls.clean_text(query)
        if clean_query != query:
            variations.append(clean_query)
        
        # Extract keywords
        keywords = cls.extract_keywords(query, top_n=5)
        if keywords:
            variations.append(" ".join(keywords))
        
        # Expand with synonyms
        expanded = cls.expand_query(query)
        variations.extend(expanded)
        
        # Remove duplicates
        variations = list(dict.fromkeys(variations))
        
        return variations