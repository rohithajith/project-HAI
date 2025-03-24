"""
Tests for the text processor module.
"""

import pytest
from rag.processor import TextProcessor

class TestTextProcessor:
    """Test cases for the TextProcessor class."""
    
    def test_chunk_text(self):
        """Test chunking text into smaller pieces."""
        # Test input
        text = "This is a test text. It has multiple sentences. " * 10
        
        # Test with default parameters
        chunks = TextProcessor.chunk_text(text)
        assert len(chunks) > 1, "Text should be split into multiple chunks"
        
        # Test with custom chunk size and overlap
        chunks = TextProcessor.chunk_text(text, chunk_size=10, overlap=2)
        assert len(chunks) > len(TextProcessor.chunk_text(text)), "Smaller chunk size should result in more chunks"
        
        # Test with empty text
        chunks = TextProcessor.chunk_text("")
        assert len(chunks) == 1, "Empty text should result in a single empty chunk"
        assert chunks[0] == "", "Empty text should result in an empty chunk"
    
    def test_clean_text(self):
        """Test cleaning text."""
        # Test with extra whitespace
        text = "  This   has  extra   spaces.  "
        cleaned = TextProcessor.clean_text(text)
        assert cleaned == "This has extra spaces.", "Extra whitespace should be removed"
        
        # Test with special characters
        text = "This has special characters: @#$%^&*()!"
        cleaned = TextProcessor.clean_text(text)
        assert "special characters" in cleaned, "Important words should be preserved"
        assert "@#$%^&" not in cleaned, "Special characters should be removed"
        
        # Test with preserved punctuation
        text = "Hello, world! How are you? I'm fine; thanks."
        cleaned = TextProcessor.clean_text(text)
        assert "Hello, world! How are you? I'm fine; thanks." == cleaned, "Important punctuation should be preserved"
    
    def test_extract_metadata(self):
        """Test extracting metadata from text."""
        # Test room category
        text = "This room has a king-size bed and a balcony."
        metadata = TextProcessor.extract_metadata(text)
        assert metadata["category"] == "rooms", "Text about rooms should be categorized as 'rooms'"
        
        # Test dining category
        text = "The restaurant serves breakfast from 7 AM to 10 AM."
        metadata = TextProcessor.extract_metadata(text)
        assert metadata["category"] == "dining", "Text about dining should be categorized as 'dining'"
        
        # Test spa category
        text = "Our spa offers various massage treatments."
        metadata = TextProcessor.extract_metadata(text)
        assert metadata["category"] == "spa", "Text about spa should be categorized as 'spa'"
        
        # Test facilities category
        text = "The fitness center is open 24/7."
        metadata = TextProcessor.extract_metadata(text)
        assert metadata["category"] == "facilities", "Text about facilities should be categorized as 'facilities'"
        
        # Test policies category
        text = "Check-in time is 3 PM and check-out time is 11 AM."
        metadata = TextProcessor.extract_metadata(text)
        assert metadata["category"] == "policies", "Text about check-in/out should be categorized as 'policies'"
        
        # Test general category (fallback)
        text = "Thank you for choosing our hotel."
        metadata = TextProcessor.extract_metadata(text)
        assert metadata["category"] == "general", "Text without specific keywords should be categorized as 'general'"
    
    def test_preprocess_query(self):
        """Test preprocessing queries."""
        # Test removing question words
        query = "What is the check-in time?"
        processed = TextProcessor.preprocess_query(query)
        assert processed == "check-in time", "Question words should be removed"
        
        # Test removing common prefixes
        query = "Can you tell me about the restaurant?"
        processed = TextProcessor.preprocess_query(query)
        assert processed == "restaurant", "Common prefixes should be removed"
        
        # Test removing trailing punctuation
        query = "Where is the gym located?"
        processed = TextProcessor.preprocess_query(query)
        assert processed == "gym located", "Trailing punctuation should be removed"
        
        # Test with multiple transformations
        query = "Could you please tell me what time the pool opens?"
        processed = TextProcessor.preprocess_query(query)
        assert "please" not in processed, "Common prefixes should be removed"
        assert processed.endswith("pool opens"), "Core query should be preserved"