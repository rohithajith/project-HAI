from typing import List, Dict, Any
from datetime import datetime, timezone
import json
import os

class ConversationMemory:
    def __init__(self, max_history_length=10, summary_threshold=15):
        self.conversation_history = []
        self.max_history_length = max_history_length
        self.summary_threshold = summary_threshold
        self.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.summaries = []
        
    def add_message(self, role: str, content: str, agent: str = None):
        """Add a new message to the conversation history"""
        message = {
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent
        }
        self.conversation_history.append(message)
        
        # If history exceeds threshold, summarize older messages
        if len(self.conversation_history) > self.summary_threshold:
            self._summarize_oldest_messages()
            
        # Save conversation to disk
        self._save_conversation()
        
    def get_formatted_history(self, max_tokens=1024) -> str:
        """Get formatted conversation history for context window"""
        formatted_history = ""
        
        # Add summaries first
        if self.summaries:
            formatted_history += "Previous conversation summary:\n"
            for summary in self.summaries:
                formatted_history += f"- {summary}\n"
            formatted_history += "\n"
        
        # Add recent messages
        for message in self.conversation_history[-self.max_history_length:]:
            role = "User" if message["role"] == "user" else "Assistant"
            formatted_history += f"{role}: {message['content']}\n"
            
        return formatted_history
    
    def _summarize_oldest_messages(self):
        """Summarize oldest messages to save context window space"""
        # Take the oldest messages that exceed our window
        messages_to_summarize = self.conversation_history[:-self.max_history_length]
        
        # Create a simple summary (in a real implementation, you might use the LLM itself)
        summary = f"Conversation about {self._extract_topics(messages_to_summarize)} with {len(messages_to_summarize)} messages"
        self.summaries.append(summary)
        
        # Remove summarized messages from active history
        self.conversation_history = self.conversation_history[-self.max_history_length:]
    
    def _extract_topics(self, messages):
        """Extract main topics from messages (simplified version)"""
        # In a real implementation, this could use keyword extraction or LLM
        all_text = " ".join([m["content"] for m in messages])
        common_hotel_topics = ["room service", "maintenance", "wellness", "check-in", "booking"]
        
        found_topics = []
        for topic in common_hotel_topics:
            if topic in all_text.lower():
                found_topics.append(topic)
                
        return ", ".join(found_topics) if found_topics else "hotel services"
    
    def _save_conversation(self):
        """Save conversation to disk"""
        log_dir = os.path.join("data", "conversations")
        os.makedirs(log_dir, exist_ok=True)
        
        conversation_file = os.path.join(log_dir, f"{self.conversation_id}.json")
        
        with open(conversation_file, "w") as f:
            json.dump({
                "id": self.conversation_id,
                "summaries": self.summaries,
                "messages": self.conversation_history
            }, f, indent=2)
    
    def load_conversation(self, conversation_id):
        """Load a previous conversation"""
        conversation_file = os.path.join("data", "conversations", f"{conversation_id}.json")
        
        if os.path.exists(conversation_file):
            with open(conversation_file, "r") as f:
                data = json.load(f)
                self.conversation_id = data["id"]
                self.summaries = data["summaries"]
                self.conversation_history = data["messages"]
            return True
        return False