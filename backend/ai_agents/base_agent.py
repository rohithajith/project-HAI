from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone
import torch
import re

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
def filter_input(self, user_input: str) -> Tuple[str, bool]:
    """
    Filter user input to prevent offensive, political, or sensitive content.
    
    Args:
        user_input: The raw user input
        
    Returns:
        Tuple containing:
        - Filtered input (or original if no issues found)
        - Boolean indicating if content was filtered
    """
    # List of patterns to filter (can be expanded)
    offensive_patterns = [
        r'\b(hate|kill|murder|attack|bomb|terrorist|suicide)\b',
        r'\b(racist|sexist|homophobic|transphobic)\b',
        r'\b(nazi|hitler|genocide)\b',
        r'\b(f[*u]ck|sh[*i]t|b[*i]tch|c[*u]nt|a[*s]s|d[*i]ck)\b',
        r'\b(porn|nude|naked|sex|xxx)\b'
    ]
    
    political_patterns = [
        r'\b(democrat|republican|liberal|conservative|socialism|communism|fascism)\b',
        r'\b(trump|biden|obama|clinton|bush|election|vote|ballot)\b',
        r'\b(congress|senate|parliament|president|prime minister|politician)\b',
        r'\b(protest|riot|revolution|coup|insurrection)\b'
    ]
    
    sensitive_patterns = [
        r'\b(hack|exploit|vulnerability|bypass|crack|steal|fraud)\b',
        r'\b(credit card|social security|passport|identity theft)\b',
        r'\b(illegal|criminal|crime|drugs|cocaine|heroin|marijuana)\b',
        r'\b(weapon|gun|rifle|pistol|firearm|ammunition)\b'
    ]
    
    # Combine all patterns
    all_patterns = offensive_patterns + political_patterns + sensitive_patterns
    
    # Check if any pattern matches
    for pattern in all_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            # Content was filtered
            return self._get_safe_input_response(), True
    
    # No issues found, return original input
    return user_input, False

def filter_output(self, model_output: str) -> Tuple[str, bool]:
    """
    Filter model output to prevent offensive, political, or sensitive content.
    
    Args:
        model_output: The raw model output
        
    Returns:
        Tuple containing:
        - Filtered output (or original if no issues found)
        - Boolean indicating if content was filtered
    """
    # List of patterns to filter (can be expanded)
    offensive_patterns = [
        r'\b(hate|kill|murder|attack|bomb|terrorist|suicide)\b',
        r'\b(racist|sexist|homophobic|transphobic)\b',
        r'\b(nazi|hitler|genocide)\b',
        r'\b(f[*u]ck|sh[*i]t|b[*i]tch|c[*u]nt|a[*s]s|d[*i]ck)\b',
        r'\b(porn|nude|naked|sex|xxx)\b'
    ]
    
    political_patterns = [
        r'\b(democrat|republican|liberal|conservative|socialism|communism|fascism)\b',
        r'\b(trump|biden|obama|clinton|bush|election|vote|ballot)\b',
        r'\b(congress|senate|parliament|president|prime minister|politician)\b',
        r'\b(protest|riot|revolution|coup|insurrection)\b'
    ]
    
    sensitive_patterns = [
        r'\b(hack|exploit|vulnerability|bypass|crack|steal|fraud)\b',
        r'\b(credit card|social security|passport|identity theft)\b',
        r'\b(illegal|criminal|crime|drugs|cocaine|heroin|marijuana)\b',
        r'\b(weapon|gun|rifle|pistol|firearm|ammunition)\b'
    ]
    
    # Combine all patterns
    all_patterns = offensive_patterns + political_patterns + sensitive_patterns
    
    # Check if any pattern matches
    for pattern in all_patterns:
        if re.search(pattern, model_output, re.IGNORECASE):
            # Content was filtered
            return self._get_safe_output_response(), True
    
    # No issues found, return original output
    return model_output, False

def _get_safe_input_response(self) -> str:
    """
    Return a safe alternative to filtered user input.
    """
    return "I need assistance with a hotel-related matter."

def _get_safe_output_response(self) -> str:
    """
    Return a safe alternative to filtered model output.
    """
    return "I apologize, but I'm not able to respond to that request. As a hotel assistant, I'm here to help with hotel-related inquiries, reservations, amenities, and local recommendations. How else may I assist you with your stay?"

def generate_response(self, user_input: str, memory, system_prompt: str = None) -> str:
    if system_prompt is None:
        system_prompt = (
            "You are an AI assistant for a hotel. "
            "Respond to guests politely and efficiently. "
            "You have access to tools to call where required based on user query."
        )
    
    # Filter user input
    filtered_input, was_input_filtered = self.filter_input(user_input)
    
    # If input was filtered, return safe response directly
    if was_input_filtered:
        return self._get_safe_output_response()
    
    # Get conversation history from memory
    conversation_context = memory.get_formatted_history()
    
    # Create a prompt with history and system instructions
    full_prompt = f"<|system|>\n{system_prompt}\n\nConversation history:\n{conversation_context}\n<|user|>\n{filtered_input}\n<|assistant|>\n"

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
        
        # Filter the model output
        filtered_output, was_output_filtered = self.filter_output(assistant_response)
        return filtered_output
    else:
        # Fallback if the expected format is not found
        fallback_response = full_response
        # Still filter the fallback response
        filtered_fallback, _ = self.filter_output(fallback_response)
        return filtered_fallback
            return full_response