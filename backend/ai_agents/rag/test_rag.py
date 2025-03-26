import sys
import os

# Ensure backend path is available for schema imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Ensure current folder is added for embedding generator
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from schemas.agent_schemas import (
    CheckInInput, CheckInOutput,
    RoomServiceInput, RoomServiceOutput,
    WellnessInput, WellnessOutput,
    EntertainmentInput, EntertainmentOutput,
    CabBookingInput, CabBookingOutput,
    ExtendStayInput, ExtendStayOutput
)
from schemas.base import AgentInput, AgentOutput, AgentMessage, ConversationState
from embedding_utils import EmbeddingGenerator
embedder = EmbeddingGenerator(model_name="finetuned_merged")
embeddings = embedder.generate(["Hello world", "How are you?"])
print("Embedding preview:", embeddings[0][:10])