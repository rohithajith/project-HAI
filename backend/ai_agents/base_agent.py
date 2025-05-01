from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional, Callable
from datetime import datetime, timezone
import torch
import re
import os

from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain.tools import Tool
from langchain_core.pydantic_v1 import BaseModel as LangChainBaseModel

class ToolDefinition:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

class AgentOutput:
    def __init__(self, response: str, tool_calls: Optional[List[Dict[str, Any]]] = None):
        self.response = response
        self.tool_calls = tool_calls or []

class LangChainToolWrapper:
    """
    Utility class for creating LangChain-compatible tools with standardized error handling.
    """
    @staticmethod
    def wrap_tool(
        func: Callable, 
        name: str, 
        description: str
    ) -> BaseTool:
        """
        Wrap a function as a LangChain Tool with standardized error handling.
        
        Args:
            func (Callable): The function to wrap
            name (str): Name of the tool
            description (str): Description of the tool's purpose
        
        Returns:
            BaseTool: A LangChain-compatible tool
        """
        def safe_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return f"Tool execution error: {str(e)}"
        
        return Tool(
            name=name,
            description=description,
            func=safe_func
        )

class BaseAgent(ABC):
    def __init__(self, name: str, model, tokenizer):
        self.name = name
        self.model = model
        self.tokenizer = tokenizer
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.priority = 0  # Default priority
        self.description = self.load_prompt("backend/ai_agents/descriptions/base_agent_description.txt")
        self.system_prompt = self.load_prompt("base_agent_prompt.txt")

    @staticmethod
    def load_prompt(filepath: str, context: str = "") -> str:
        """
        Load a system prompt from a text file.
        
        Args:
            filepath (str): Name of the prompt file in the prompts directory
            context (str, optional): Context to replace {context} in the prompt. Defaults to "".
        
        Returns:
            str: The loaded prompt with optional context substitution
        """
        try:
            prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', filepath)
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read().strip()
            
            # Replace {context} if provided
            return prompt_template.format(context=context)
        except FileNotFoundError:
            print(f"Warning: Prompt file {filepath} not found. Using default prompt.")
            return "You are an AI assistant helping with hotel-related tasks."
        except Exception as e:
            print(f"Error loading prompt {filepath}: {e}")
            return "You are an AI assistant helping with hotel-related tasks."

    @abstractmethod
    def should_handle(self, message: str) -> bool:
        pass

    @abstractmethod
    def process(self, message: str, memory) -> Dict[str, Any]:
        pass

    def get_available_tools(self) -> List[BaseTool]:
        """
        Returns a list of tools available for this agent.
        Subclasses should override this method.
        
        Returns:
            List[BaseTool]: Available tools for the agent
        """
        return []

    def get_keywords(self) -> List[str]:
        """
        Default implementation returns an empty list of keywords.
        Agents should override this method to provide their specific keywords.
        
        Returns:
            List[str]: Keywords associated with the agent
        """
        return []

    def handle_tool_call(self, tool_name: str, **kwargs) -> Any:
        """
        Default tool call handler with a generic admin notification tool.
        
        Args:
            tool_name (str): Name of the tool to call
            **kwargs: Additional parameters for the tool
        
        Returns:
            Any: Result of the tool call
        """
        if tool_name == "notify_admin_dashboard":
            emergency_details = kwargs.get('emergency_details', {})
            print(f"EMERGENCY NOTIFICATION: {emergency_details}")
            return {"status": "success", "message": "Admin dashboard notified"}
        
        raise NotImplementedError(f"Tool '{tool_name}' not implemented for {self.name}")

    def format_output(self, response: str, tool_calls: Optional[List[Dict[str, Any]]] = None, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Format the agent's output with a consistent structure.
        
        Args:
            response (str): The response text
            tool_calls (Optional[List[Dict[str, Any]]]): List of tool calls
            agent_name (Optional[str]): Name of the agent
        
        Returns:
            Dict[str, Any]: Formatted output dictionary
        """
        tool_calls = tool_calls or []
        
        return {
            "response": response,
            "tool_calls": tool_calls,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent_name or self.name
        }

    def filter_input(self, user_input: str) -> Tuple[str, bool]:
        """
        Filter user input to prevent offensive, political, or sensitive content.
        
        Args:
            user_input (str): The input to filter
        
        Returns:
            Tuple[str, bool]: Filtered input and a flag indicating if input was filtered
        """
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
        
        all_patterns = offensive_patterns + political_patterns + sensitive_patterns
        
        for pattern in all_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return self._get_safe_input_response(), True
        
        return user_input, False

    def _get_safe_input_response(self) -> str:
        """
        Return a safe alternative to filtered user input.
        
        Returns:
            str: A safe, generic input response
        """
        return "I need assistance with a hotel-related matter."

    def generate_response(self, user_input: str, memory, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response using the agent's model and conversation context.
        
        Args:
            user_input (str): The user's input
            memory: Conversation memory
            system_prompt (Optional[str]): Custom system prompt
        
        Returns:
            str: Generated response
        """
        if system_prompt is None:
            system_prompt = (
                "You are an AI assistant for a hotel. "
                "Respond to guests politely and efficiently. "
                "You have access to tools to call like room service, SOS emergency, maintenance request, service booking, wellness agents."
            )
        
        # Filter user input
        filtered_input, was_input_filtered = self.filter_input(user_input)
        
        if was_input_filtered:
            return self._get_safe_input_response()
        
        # Get conversation history from memory
        conversation_context = memory.get_formatted_history() if memory else ""
        
        # Create a prompt with history and system instructions
        full_prompt = f"<|system|>\n{system_prompt}\n\nConversation history:\n{conversation_context}\n<|user|>\n{filtered_input}\n<|assistant|>\n"
    
        inputs = self.tokenizer(full_prompt, return_tensors="pt", truncation=True, max_length=1024)
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
    
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.7,
                top_k=50,
                top_p=0.9,
                repetition_penalty=1.2,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the assistant's response part
        if "<|assistant|>" in full_response:
            assistant_response = full_response.split("<|assistant|>")[-1].strip()
            return assistant_response
        else:
            return full_response