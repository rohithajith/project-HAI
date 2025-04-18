from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
import json
import os
import re
import uuid

class ConversationMemory:
    def __init__(self, max_history_length=10, summary_threshold=15):
        self.conversation_history = []
        self.max_history_length = max_history_length
        self.summary_threshold = summary_threshold
        self.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.summaries = []
        # GDPR related attributes
        self.consent_status = "pending"  # Options: pending, granted, denied
        self.data_purposes = ["customer_service"]  # Default purpose
        self.retention_period = 90  # Default retention in days
        self.data_subject_id = str(uuid.uuid4())  # Anonymous identifier
        
    def add_message(self, role: str, content: str, agent: str = None):
        """Add a new message to the conversation history with GDPR compliance"""
        # Anonymize personal data if it's a user message
        if role == "user":
            anonymized_content = self._anonymize_personal_data(content)
        else:
            anonymized_content = content
            
        # Calculate retention date
        retention_date = (datetime.now(timezone.utc) + timedelta(days=self.retention_period)).isoformat()
        
        message = {
            "id": str(uuid.uuid4()),  # Unique identifier for each message
            "role": role,  # "user" or "assistant"
            "content": anonymized_content,
            "original_length": len(content),  # Store original length for analytics without content
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent,
            "gdpr_metadata": {
                "retention_date": retention_date,
                "purposes": self.data_purposes.copy(),
                "consent_status": self.consent_status,
                "data_subject_id": self.data_subject_id,
                "anonymized": (role == "user")  # Flag indicating if content was anonymized
            }
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
    
    def _anonymize_personal_data(self, text: str) -> str:
        """
        Anonymize personal identifiable information in text.
        
        Args:
            text: The text to anonymize
            
        Returns:
            Anonymized text with personal data replaced
        """
        # Patterns for common personal data
        patterns = [
            # Phone numbers (various formats)
            (r'\b(?:\+\d{1,3}[-\s]?)?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}\b', '[PHONE_NUMBER]'),
            
            # Email addresses
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_ADDRESS]'),
            
            # Credit card numbers (simplified pattern)
            (r'\b(?:\d{4}[-\s]?){3}\d{4}\b', '[PAYMENT_CARD]'),
            
            # Names (common title + name pattern, simplified)
            (r'\b(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+[A-Z][a-z]+\b', '[NAME]'),
            
            # Room numbers
            (r'\b(?:room|suite)\s+\d+\b', '[ROOM_NUMBER]'),
            
            # Addresses (simplified pattern)
            (r'\b\d+\s+[A-Za-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b', '[ADDRESS]'),
            
            # Social Security Numbers (US)
            (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),
            
            # Passport numbers (simplified pattern)
            (r'\b[A-Z]{1,2}\d{6,9}\b', '[PASSPORT_NUMBER]')
        ]
        
        # Apply each pattern
        anonymized_text = text
        for pattern, replacement in patterns:
            anonymized_text = re.sub(pattern, replacement, anonymized_text, flags=re.IGNORECASE)
            
        return anonymized_text
    
    def _save_conversation(self):
        """Save conversation to disk with GDPR compliance"""
        # Create directory structure that separates data by date for easier retention management
        year_month = datetime.now().strftime('%Y-%m')
        log_dir = os.path.join("data", "conversations", year_month)
        os.makedirs(log_dir, exist_ok=True)
        
        conversation_file = os.path.join(log_dir, f"{self.conversation_id}.json")
        
        # Add GDPR metadata to the conversation record
        conversation_data = {
            "id": self.conversation_id,
            "data_subject_id": self.data_subject_id,
            "summaries": self.summaries,
            "messages": self.conversation_history,
            "gdpr_metadata": {
                "creation_date": datetime.now(timezone.utc).isoformat(),
                "retention_date": (datetime.now(timezone.utc) + timedelta(days=self.retention_period)).isoformat(),
                "purposes": self.data_purposes,
                "consent_status": self.consent_status,
                "data_controller": "Hotel AI System",
                "legal_basis": "legitimate_interest",  # or "consent", "contract", etc.
                "data_subject_rights_url": "/api/user/data/rights"
            }
        }
        
        with open(conversation_file, "w") as f:
            json.dump(conversation_data, f, indent=2)
    
    def load_conversation(self, conversation_id):
        """Load a previous conversation with GDPR checks"""
        # First try to find the conversation in the current month's directory
        current_year_month = datetime.now().strftime('%Y-%m')
        conversation_file = os.path.join("data", "conversations", current_year_month, f"{conversation_id}.json")
        
        # If not found, search in previous months (up to 12 months back)
        if not os.path.exists(conversation_file):
            for i in range(1, 13):
                # Calculate previous month
                date = datetime.now() - timedelta(days=30*i)
                year_month = date.strftime('%Y-%m')
                alt_path = os.path.join("data", "conversations", year_month, f"{conversation_id}.json")
                if os.path.exists(alt_path):
                    conversation_file = alt_path
                    break
        
        if os.path.exists(conversation_file):
            with open(conversation_file, "r") as f:
                data = json.load(f)
                
                # Check if the conversation has expired based on retention date
                if "gdpr_metadata" in data and "retention_date" in data["gdpr_metadata"]:
                    retention_date = datetime.fromisoformat(data["gdpr_metadata"]["retention_date"])
                    if datetime.now(timezone.utc) > retention_date:
                        # Data has expired, should be deleted
                        os.remove(conversation_file)
                        return False
                
                # Load the conversation data
                self.conversation_id = data["id"]
                self.summaries = data["summaries"]
                self.conversation_history = data["messages"]
                
                # Load GDPR metadata if available
                if "gdpr_metadata" in data:
                    if "purposes" in data["gdpr_metadata"]:
                        self.data_purposes = data["gdpr_metadata"]["purposes"]
                    if "consent_status" in data["gdpr_metadata"]:
                        self.consent_status = data["gdpr_metadata"]["consent_status"]
                    if "retention_date" in data["gdpr_metadata"]:
                        # Calculate remaining days for retention period
                        retention_date = datetime.fromisoformat(data["gdpr_metadata"]["retention_date"])
                        self.retention_period = (retention_date - datetime.now(timezone.utc)).days
                
                # Load data subject ID if available
                if "data_subject_id" in data:
                    self.data_subject_id = data["data_subject_id"]
                
                return True
        return False
        
    def update_consent(self, status, purposes=None):
        """Update consent status and purposes"""
        self.consent_status = status
        if purposes:
            self.data_purposes = purposes
        
        # Update all messages with new consent information
        for message in self.conversation_history:
            if "gdpr_metadata" in message:
                message["gdpr_metadata"]["consent_status"] = status
                if purposes:
                    message["gdpr_metadata"]["purposes"] = purposes.copy()
        
        # Save the updated conversation
        self._save_conversation()
        return True
    
    def delete_data(self):
        """Delete all data for this conversation (Right to Erasure)"""
        # Find all possible locations of the conversation file
        for i in range(0, 13):  # Current month + 12 previous months
            date = datetime.now() - timedelta(days=30*i)
            year_month = date.strftime('%Y-%m')
            conversation_file = os.path.join("data", "conversations", year_month, f"{self.conversation_id}.json")
            if os.path.exists(conversation_file):
                os.remove(conversation_file)
                
        # Clear memory
        self.conversation_history = []
        self.summaries = []
        
        # Generate a new conversation ID and data subject ID
        self.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.data_subject_id = str(uuid.uuid4())
        
        return True