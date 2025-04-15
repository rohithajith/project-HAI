import os
from typing import List, Tuple, Dict

class ImprovedRAGHelper:
    def __init__(self, file_paths: List[str]):
        """
        Initialize the RAG helper with multiple file paths
        
        Args:
            file_paths: List of relative file paths from project root
        """
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.file_contents = {}
        
        for file_path in file_paths:
            full_path = os.path.join(self.base_dir, file_path)
            self.file_contents[file_path] = self.load_data(full_path)
    
    def load_data(self, file_path: str) -> str:
        """Load data from a file"""
        if not os.path.exists(file_path):
            print(f"[WARN] File not found: {file_path}")
            return "Default hotel info."
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def get_relevant_passages(self, query: str, min_score: float = 0.4, k: int = 3) -> List[Tuple[str, float]]:
        """
        Get passages relevant to the query from all loaded files
        
        Args:
            query: The user query
            min_score: Minimum relevance score (0-1) for a passage to be included
            k: Maximum number of passages to return
            
        Returns:
            List of (passage, score) tuples sorted by relevance
        """
        if not query or len(query.strip()) == 0:
            return []
            
        # Preprocess query
        query_words = set(query.lower().split())
        query_keywords = self._extract_keywords(query.lower())
        
        # Extract the most important keyword for focused search
        primary_keyword = self._get_primary_keyword(query.lower())
        
        all_scored_lines = []
        
        # Process each file
        for file_path, content in self.file_contents.items():
            # First split into sections
            sections = content.split('\n\n')
            
            for section in sections:
                if not section.strip():
                    continue
                
                # Get section header if present
                section_lines = section.split('\n')
                section_header = section_lines[0].lower() if section_lines else ""
                has_header = ':' in section_header
                
                # Check if section header is highly relevant
                header_relevant = False
                if has_header:
                    for keyword in query_keywords:
                        if keyword in section_header:
                            header_relevant = True
                            break
                
                # Process each line in the section
                for i, line in enumerate(section_lines):
                    # Skip empty lines
                    if not line.strip():
                        continue
                        
                    line_lower = line.lower()
                    
                    # Skip processing section header separately
                    if i == 0 and has_header:
                        # Only include header if it's directly relevant
                        if header_relevant:
                            all_scored_lines.append((line, 0.9))  # High score for relevant headers
                        continue
                    
                    # Calculate line relevance
                    line_words = set(line_lower.split())
                    
                    # Basic word overlap
                    word_overlap_score = len(query_words.intersection(line_words)) / len(query_words) if query_words else 0
                    
                    # Keyword match (weighted higher)
                    keyword_score = 0
                    for keyword in query_keywords:
                        if keyword in line_lower:
                            keyword_score += 1
                    keyword_score = keyword_score / len(query_keywords) if query_keywords else 0
                    
                    # Primary keyword exact match (highest weight)
                    primary_match = 1.0 if primary_keyword and primary_keyword in line_lower else 0
                    
                    # Header context bonus (small bonus if the section header is relevant)
                    header_bonus = 0.1 if header_relevant else 0
                    
                    # Combined score (weighted)
                    combined_score = (0.2 * word_overlap_score) + (0.3 * keyword_score) + (0.4 * primary_match) + header_bonus
                
                    # Only include lines that meet the threshold
                    if combined_score >= min_score:
                        all_scored_lines.append((line, combined_score))
        
        # Sort by score and return top k lines
        sorted_lines = sorted(all_scored_lines, key=lambda x: x[1], reverse=True)[:k]
        
        # Group consecutive lines from the same section together for better context
        result = []
        current_section = []
        current_score = 0
        
        for line, score in sorted_lines:
            # If this is a section header or we're starting a new group
            if ':' in line or not current_section:
                # Save previous section if it exists
                if current_section:
                    result.append(('\n'.join(current_section), current_score))
                    current_section = []
                
                # Start new section
                current_section.append(line)
                current_score = score
            else:
                # Add to current section
                current_section.append(line)
                # Update score (average)
                current_score = (current_score + score) / 2
        
        # Add the last section if it exists
        if current_section:
            result.append(('\n'.join(current_section), current_score))
        
        return result
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from the query"""
        # Common hotel-related keywords to look for
        hotel_keywords = [
            "spa", "wellness", "massage", "facial", "sauna", "steam", "treatment",
            "breakfast", "buffet", "restaurant", "dining", "food", "menu",
            "check-in", "check-out", "reservation", "booking", "cancel",
            "pool", "gym", "fitness", "parking", "wifi", "internet",
            "pet", "smoking", "policy", "fee", "charge", "payment",
            "room", "suite", "bed", "accessibility", "service", "hours",
            "open", "time", "available", "price", "cost", "rate"
        ]
        
        # Extract words from query that match our keywords
        query_words = query.split()
        extracted_keywords = []
        
        for word in query_words:
            word = word.strip(".,?!").lower()
            if word in hotel_keywords:
                extracted_keywords.append(word)
        
        # If no keywords found, use all words as fallback
        if not extracted_keywords and query_words:
            extracted_keywords = [w.strip(".,?!").lower() for w in query_words]
            
        return extracted_keywords
        
    def _get_primary_keyword(self, query: str) -> str:
        """Extract the most important keyword from the query"""
        # Priority keywords (ordered by importance)
        priority_keywords = [
            "spa", "wellness", "massage", "breakfast", "buffet", "restaurant",
            "check-in", "check-out", "reservation", "booking", "pool", "gym",
            "pet", "smoking", "wifi", "internet", "room", "suite"
        ]
        
        # Check for each priority keyword in the query
        for keyword in priority_keywords:
            if keyword in query:
                return keyword
                
        # If no priority keyword found, use the first extracted keyword
        extracted = self._extract_keywords(query)
        return extracted[0] if extracted else ""

# Initialize with both information files
rag_helper = ImprovedRAGHelper([
    'data/hotel_info/hotel_information.txt',
    'data/hotel_info/hotel_policies.txt'
])