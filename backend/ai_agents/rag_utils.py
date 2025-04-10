import os
from typing import List, Tuple

class SimpleRAGHelper:
    def __init__(self, relative_file_path: str):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.file_path = os.path.join(base_dir, relative_file_path)
        self.content = self.load_data()

    def load_data(self) -> str:
        if not os.path.exists(self.file_path):
            print(f"[WARN] File not found: {self.file_path}")
            return "Default hotel info."
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def get_relevant_passages(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        query_words = set(query.lower().split())
        passages = self.content.split('\n\n')
        
        scored_passages = []
        for passage in passages:
            passage_words = set(passage.lower().split())
            if not query_words:
                score = 0
            else:
                score = len(query_words.intersection(passage_words)) / len(query_words)
            scored_passages.append((passage, score))
        
        return sorted(scored_passages, key=lambda x: x[1], reverse=True)[:k]

# Initialize with correct relative path from project root
rag_helper = SimpleRAGHelper('data/hotel_info/hotel_information.txt')