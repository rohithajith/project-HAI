from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, time
from pathlib import Path
import json
from .base_agent import BaseAgent, AgentOutput, ToolDefinition, ToolParameters, ToolParameterProperty

class PromotionalContent(BaseModel):
    """Schema for promotional content."""
    title: str = Field(..., description="Title of the promotion")
    description: str = Field(..., description="Detailed description")
    start_date: datetime = Field(..., description="Start date and time")
    end_date: datetime = Field(..., description="End date and time")
    category: str = Field(..., description="Category (theme_night, happy_hour, etc)")
    target_audience: Optional[List[str]] = Field(None, description="Target audience segments")

class RAGDocument(BaseModel):
    """Schema for RAG document storage."""
    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding")

class PromotionAgent(BaseAgent):
    """Agent responsible for promoting theme nights and happy hours using RAG."""
    
    def __init__(self):
        self.name = "promotion_agent"
        self.priority = 5  # Medium priority for promotional content
        
        # Initialize RAG storage
        self.rag_documents: List[RAGDocument] = []
        self.embeddings_file = Path("data/promotion_embeddings.json")
        self._load_embeddings()
        
        # Define available tools
        self.tools = [
            ToolDefinition(
                name="add_promotional_content",
                description="Add new promotional content with RAG",
                parameters=ToolParameters(
                    type="object",
                    properties={
                        "content_file": ToolParameterProperty(
                            type="string",
                            description="Path to content file"
                        ),
                        "category": ToolParameterProperty(
                            type="string",
                            description="Content category",
                            enum=["theme_night", "happy_hour", "special_event"]
                        ),
                        "metadata": ToolParameterProperty(
                            type="object",
                            description="Additional metadata"
                        )
                    },
                    required=["content_file", "category"]
                )
            ),
            ToolDefinition(
                name="query_promotions",
                description="Query promotional content using RAG",
                parameters=ToolParameters(
                    type="object",
                    properties={
                        "query": ToolParameterProperty(
                            type="string",
                            description="Search query"
                        ),
                        "category": ToolParameterProperty(
                            type="string",
                            description="Optional category filter"
                        )
                    },
                    required=["query"]
                )
            )
        ]

    def _load_embeddings(self):
        """Load existing RAG embeddings from file."""
        try:
            if self.embeddings_file.exists():
                with open(self.embeddings_file, 'r') as f:
                    data = json.load(f)
                    self.rag_documents = [RAGDocument(**doc) for doc in data]
        except Exception as e:
            print(f"Error loading embeddings: {e}")
            self.rag_documents = []

    def _save_embeddings(self):
        """Save RAG embeddings to file."""
        try:
            self.embeddings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.embeddings_file, 'w') as f:
                json.dump([doc.model_dump() for doc in self.rag_documents], f)
        except Exception as e:
            print(f"Error saving embeddings: {e}")

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using local model."""
        # TODO: Implement local embedding generation
        # This should use a local embedding model like SentenceTransformers
        # For now, return a simple mock embedding
        return [0.0] * 384  # Placeholder 384-dim embedding

    async def _add_document(self, content: str, metadata: Dict[str, Any]):
        """Add a new document to RAG storage."""
        embedding = await self._generate_embedding(content)
        document = RAGDocument(
            content=content,
            metadata=metadata,
            embedding=embedding
        )
        self.rag_documents.append(document)
        self._save_embeddings()

    async def _query_similar(self, query: str, top_k: int = 3) -> List[RAGDocument]:
        """Query similar documents using RAG."""
        if not self.rag_documents:
            return []

        query_embedding = await self._generate_embedding(query)
        
        # Compute similarities and sort
        similarities = []
        for doc in self.rag_documents:
            if doc.embedding:
                # Compute cosine similarity
                similarity = sum(a * b for a, b in zip(query_embedding, doc.embedding))
                similarities.append((similarity, doc))
        
        # Sort by similarity and return top_k
        similarities.sort(reverse=True, key=lambda x: x[0])
        return [doc for _, doc in similarities[:top_k]]

    def should_handle(self, message: str, history: List[Dict[str, Any]]) -> bool:
        """Determine if this agent should handle the message."""
        promotion_keywords = [
            "promotion", "theme night", "happy hour", "special event",
            "deal", "discount", "offer", "what's on", "entertainment",
            "events", "activities", "tonight", "schedule"
        ]
        
        message_lower = message.lower()
        
        # Check for promotion keywords
        has_keywords = any(keyword in message_lower for keyword in promotion_keywords)
        
        # Check if we're in an ongoing promotion conversation
        in_conversation = self._is_in_promotion_conversation(history)
        
        return has_keywords or in_conversation

    async def process(self, message: str, history: List[Dict[str, Any]]) -> AgentOutput:
        """Process promotion related requests."""
        # Content filtering
        if self._contains_harmful_content(message):
            return AgentOutput(
                response="I apologize, but I cannot process messages containing inappropriate "
                        "content. How else may I assist you with our promotions and events?"
            )

        # Determine request type and handle accordingly
        if self._is_theme_night_query(message):
            return await self._handle_theme_night_query(message)
        elif self._is_happy_hour_query(message):
            return await self._handle_happy_hour_query(message)
        elif self._is_event_schedule_query(message):
            return await self._handle_event_schedule_query(message)
        else:
            return await self._handle_general_promotion_query(message)

    def _contains_harmful_content(self, message: str) -> bool:
        """Check for harmful or inappropriate content."""
        harmful_keywords = [
            "lgbtq", "rape", "bomb", "terror", "politics",
            "weapon", "drugs", "explicit", "offensive"
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in harmful_keywords)

    def _is_in_promotion_conversation(self, history: List[Dict[str, Any]]) -> bool:
        """Check if we're in an ongoing promotion conversation."""
        if not history:
            return False
            
        recent_history = history[-3:]  # Look at last 3 messages
        for entry in recent_history:
            if entry.get('agent') == self.name:
                return True
        return False

    def _is_theme_night_query(self, message: str) -> bool:
        """Check if message is asking about theme nights."""
        theme_keywords = ["theme night", "special night", "entertainment", "show"]
        return any(keyword in message.lower() for keyword in theme_keywords)

    def _is_happy_hour_query(self, message: str) -> bool:
        """Check if message is asking about happy hours."""
        happy_hour_keywords = ["happy hour", "drinks", "specials", "discount"]
        return any(keyword in message.lower() for keyword in happy_hour_keywords)

    def _is_event_schedule_query(self, message: str) -> bool:
        """Check if message is asking about event schedules."""
        schedule_keywords = ["schedule", "when", "what time", "tonight", "upcoming"]
        return any(keyword in message.lower() for keyword in schedule_keywords)

    async def _handle_theme_night_query(self, message: str) -> AgentOutput:
        """Handle theme night related queries using RAG."""
        similar_docs = await self._query_similar(message)
        
        if not similar_docs:
            return AgentOutput(
                response="I don't have any current theme night information. Please check "
                        "back later for updates on our special themed events."
            )
        
        # Construct response from similar documents
        response = "Here are our upcoming theme nights:\n\n"
        for doc in similar_docs:
            if doc.metadata.get("category") == "theme_night":
                response += f"🌟 {doc.metadata.get('title', 'Special Event')}\n"
                response += f"{doc.content}\n\n"
        
        return AgentOutput(
            response=response.strip(),
            notifications=[{
                "type": "theme_night_query",
                "timestamp": datetime.utcnow().isoformat()
            }]
        )

    async def _handle_happy_hour_query(self, message: str) -> AgentOutput:
        """Handle happy hour related queries using RAG."""
        similar_docs = await self._query_similar(message)
        
        if not similar_docs:
            return AgentOutput(
                response="I don't have any current happy hour information. Please check "
                        "with our bar staff for today's specials."
            )
        
        # Construct response from similar documents
        response = "Here are our happy hour specials:\n\n"
        for doc in similar_docs:
            if doc.metadata.get("category") == "happy_hour":
                response += f"🍹 {doc.metadata.get('title', 'Happy Hour')}\n"
                response += f"{doc.content}\n\n"
        
        return AgentOutput(
            response=response.strip(),
            notifications=[{
                "type": "happy_hour_query",
                "timestamp": datetime.utcnow().isoformat()
            }]
        )

    async def _handle_event_schedule_query(self, message: str) -> AgentOutput:
        """Handle event schedule related queries using RAG."""
        similar_docs = await self._query_similar(message)
        
        if not similar_docs:
            return AgentOutput(
                response="I don't have any current event schedule information. Please check "
                        "with our concierge for the latest updates on hotel activities."
            )
        
        # Construct response from similar documents
        response = "Here's what's happening:\n\n"
        for doc in similar_docs:
            event_time = doc.metadata.get("start_time", "")
            response += f"📅 {event_time} - {doc.metadata.get('title', 'Event')}\n"
            response += f"{doc.content}\n\n"
        
        return AgentOutput(
            response=response.strip(),
            notifications=[{
                "type": "schedule_query",
                "timestamp": datetime.utcnow().isoformat()
            }]
        )

    async def _handle_general_promotion_query(self, message: str) -> AgentOutput:
        """Handle general promotion queries using RAG."""
        similar_docs = await self._query_similar(message)
        
        if not similar_docs:
            return AgentOutput(
                response="Welcome! I can help you discover our exciting events and promotions. "
                        "Would you like to know about:\n\n"
                        "1. Theme Nights & Entertainment\n"
                        "2. Happy Hour Specials\n"
                        "3. Upcoming Events Schedule\n\n"
                        "Just let me know what interests you!"
            )
        
        # Construct response from similar documents
        response = "Here are some promotions you might be interested in:\n\n"
        for doc in similar_docs:
            response += f"✨ {doc.metadata.get('title', 'Special Promotion')}\n"
            response += f"{doc.content}\n\n"
        
        return AgentOutput(
            response=response.strip(),
            notifications=[{
                "type": "general_promotion_query",
                "timestamp": datetime.utcnow().isoformat()
            }]
        )