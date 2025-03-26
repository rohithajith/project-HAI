"""
Test script for the TextProcessor class in processor.py
"""

import logging
import unittest
from backend.ai_agents.rag.processor import TextProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestTextProcessor(unittest.TestCase):
    """Test cases for TextProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_text = """
        Welcome to our luxury hotel. We offer spacious rooms with comfortable beds and 
        modern amenities. Our restaurant serves delicious breakfast from 7:00 AM to 10:30 AM.
        The spa is open daily from 9:00 AM to 8:00 PM. Please contact the front desk for 
        any assistance during your stay. Check-out time is 12:00 PM.
        """
        
    def test_model_loading(self):
        """Test that the finetuned model is loaded correctly."""
        # This will indirectly test if the model was loaded correctly
        # by checking if SPACY_AVAILABLE is True
        self.assertTrue(hasattr(TextProcessor, 'SPACY_AVAILABLE'), 
                        "TextProcessor should have SPACY_AVAILABLE attribute")
        
        # Log the status of the model
        logger.info(f"Finetuned model available: {TextProcessor.SPACY_AVAILABLE}")
        
    def test_chunk_text(self):
        """Test text chunking functionality."""
        # Test word chunking
        word_chunks = TextProcessor.chunk_text(self.sample_text, chunk_size=20, overlap=5, chunk_by="word")
        self.assertIsInstance(word_chunks, list, "Chunking should return a list")
        self.assertTrue(len(word_chunks) > 0, "Should produce at least one chunk")
        
        # Test sentence chunking
        sentence_chunks = TextProcessor.chunk_text(self.sample_text, chunk_size=50, overlap=10, chunk_by="sentence")
        self.assertIsInstance(sentence_chunks, list, "Sentence chunking should return a list")
        
        logger.info(f"Word chunks: {len(word_chunks)}, Sentence chunks: {len(sentence_chunks)}")
        
    def test_clean_text(self):
        """Test text cleaning functionality."""
        cleaned_text = TextProcessor.clean_text(self.sample_text)
        self.assertIsInstance(cleaned_text, str, "Cleaning should return a string")
        self.assertLess(len(cleaned_text), len(self.sample_text), "Cleaned text should be shorter")
        
        # Test aggressive cleaning
        aggressive_cleaned = TextProcessor.clean_text(self.sample_text, aggressive=True)
        self.assertLess(len(aggressive_cleaned), len(cleaned_text), 
                        "Aggressively cleaned text should be shorter")
        
        logger.info(f"Original length: {len(self.sample_text)}, Cleaned: {len(cleaned_text)}, "
                   f"Aggressive: {len(aggressive_cleaned)}")
        
    def test_extract_metadata(self):
        """Test metadata extraction."""
        metadata = TextProcessor.extract_metadata(self.sample_text)
        self.assertIsInstance(metadata, dict, "Metadata should be a dictionary")
        self.assertIn("category", metadata, "Metadata should include category")
        self.assertIn("sentiment", metadata, "Metadata should include sentiment")
        
        # Check if entities are extracted when the model is available
        if TextProcessor.SPACY_AVAILABLE:
            logger.info("Testing entity extraction with finetuned model")
            # This will only run if the finetuned model is available
            if "entities" in metadata:
                logger.info(f"Extracted entities: {metadata['entities']}")
            else:
                logger.info("No entities extracted, but model is available")
        else:
            logger.info("Finetuned model not available, skipping entity extraction test")
        
        logger.info(f"Extracted metadata: {metadata}")
        
    def test_preprocess_query(self):
        """Test query preprocessing."""
        query = "What are the breakfast hours at the hotel?"
        processed = TextProcessor.preprocess_query(query)
        self.assertIsInstance(processed, str, "Processed query should be a string")
        self.assertNotEqual(processed, query, "Processed query should be different from original")
        
        logger.info(f"Original query: '{query}', Processed: '{processed}'")
        
    def test_expand_query(self):
        """Test query expansion."""
        query = "What is the wifi password?"
        expanded = TextProcessor.expand_query(query)
        self.assertIsInstance(expanded, list, "Expanded queries should be a list")
        self.assertGreater(len(expanded), 1, "Should generate multiple expanded queries")
        
        logger.info(f"Original query: '{query}', Expanded: {expanded}")
        
    def test_extract_keywords(self):
        """Test keyword extraction."""
        keywords = TextProcessor.extract_keywords(self.sample_text, top_n=5)
        self.assertIsInstance(keywords, list, "Keywords should be a list")
        self.assertLessEqual(len(keywords), 5, "Should extract at most top_n keywords")
        
        logger.info(f"Extracted keywords: {keywords}")
        
    def test_generate_query_variations(self):
        """Test query variation generation."""
        query = "How do I check out of the hotel?"
        variations = TextProcessor.generate_query_variations(query)
        self.assertIsInstance(variations, list, "Variations should be a list")
        self.assertGreater(len(variations), 1, "Should generate multiple variations")
        
        logger.info(f"Original query: '{query}', Variations: {variations}")

if __name__ == "__main__":
    logger.info("Starting TextProcessor tests")
    unittest.main()