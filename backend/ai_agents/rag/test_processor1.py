import unittest
from backend.ai_agents.rag.processor import TextProcessor

class TestTextProcessor(unittest.TestCase):

    def setUp(self):
        self.sample_text = """
        Welcome to our luxury hotel! Our breakfast is served from 7:00 AM to 10:30 AM.
        The spa and wellness center opens at 9:00 AM. Check-out is at 12:00 PM.
        """
        self.sample_query = "What are the breakfast hours at the hotel?"

    def test_preprocess_query(self):
        processed = TextProcessor.preprocess_query(self.sample_query)
        self.assertIsInstance(processed, str)
        print("Processed query by LLM:", processed)

    def test_expand_query(self):
        expansions = TextProcessor.expand_query("What is the wifi password?")
        self.assertTrue(len(expansions) > 0)
        print("LLM-expanded queries:", expansions)

    def test_extract_keywords(self):
        keywords = TextProcessor.extract_keywords(self.sample_text)
        self.assertTrue(len(keywords) > 0)
        print("LLM-extracted keywords:", keywords)

    def test_generate_query_variations(self):
        variations = TextProcessor.generate_query_variations("How do I check out of the hotel?")
        self.assertTrue(len(variations) > 1)
        print("LLM-generated query variations:", variations)

    def test_extract_metadata(self):
        metadata = TextProcessor.extract_metadata(self.sample_text)
        self.assertIn("category", metadata)
        self.assertIn("sentiment", metadata)
        print("Metadata from LLM:", metadata)

if __name__ == "__main__":
    unittest.main()