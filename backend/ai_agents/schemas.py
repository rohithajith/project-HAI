from pydantic import BaseModel

class AgentMessage(BaseModel):
    content: str
    role: str

class ConversationState(BaseModel):
    history: list[AgentMessage] = []
    current_agent: str = "supervisor"