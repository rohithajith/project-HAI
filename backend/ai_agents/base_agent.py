from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime, timezone
import torch

class ToolDefinition:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

class AgentOutput:
    def __init__(self, response: str, tool_calls: List[Dict[str, Any]] = None):
        self.response = response
        self.tool_calls = tool_calls or []

class BaseAgent(ABC):
    def __init__(self, name: str, model, tokenizer):
        self.name = name
        self.model = model
        self.tokenizer = tokenizer
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @abstractmethod
    def should_handle(self, message: str) -> bool:
        pass

    @abstractmethod
    def process(self, message: str, memory) -> Dict[str, Any]:
        pass

    def get_available_tools(self) -> List[ToolDefinition]:
        return []

    def handle_tool_call(self, tool_name: str, **kwargs) -> Any:
        raise NotImplementedError(f"Tool '{tool_name}' not implemented for {self.name}")

    def format_output(self, response: str, tool_calls: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "response": response,
            "tool_calls": tool_calls or [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": self.name
        }

    def generate_response(self, user_input: str, memory, system_prompt: str = None) -> str:
        if system_prompt is None:
            system_prompt = (
                "You are an AI assistant for a hotel. "
                "Respond to guests politely and efficiently. "
                "You have access to tools to call where required based on user query."
            )
        
        # Get conversation history from memory
        conversation_context = memory.get_formatted_history()
        
        # Create a prompt with history and system instructions
        full_prompt = f"<|system|>\n{system_prompt}\n\nConversation history:\n{conversation_context}\n<|user|>\n{user_input}\n<|assistant|>\n"

        inputs = self.tokenizer(full_prompt, return_tensors="pt", truncation=True, max_length=1024)
        inputs = {key: value.to(self.device) for key, value in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=150,  # Instead of max_length
                temperature=0.7,  # Controls randomness (lower = more predictable)
                top_k=50,         # Limits low-likelihood words
                top_p=0.9,        # Nucleus sampling (removes unlikely words)
                repetition_penalty=1.2,  # Reduces repeating phrases
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the assistant's response part
        # The format is: <|system|>...<|user|>...<|assistant|>RESPONSE
        if "<|assistant|>" in full_response:
            # Extract only the text after the last <|assistant|> tag
            assistant_response = full_response.split("<|assistant|>")[-1].strip()
            return assistant_response
        else:
            # Fallback if the expected format is not found
            return full_response