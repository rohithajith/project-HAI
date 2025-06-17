from typing import Dict, Any, Optional
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LocalModelChatbot:
    """
    A chatbot implementation that uses a local language model for generating responses.
    
    This class provides a simple interface for interacting with a local language model,
    handling the loading of the model, tokenization, and response generation.
    """
    
    def __init__(
        self, 
        model_path: Optional[str] = None,
        device: str = "auto",
        load_in_8bit: bool = True,
        max_new_tokens: int = 150,
        temperature: float = 0.7,
        top_k: int = 50,
        top_p: float = 0.9,
        repetition_penalty: float = 1.2
    ):
        """
        Initialize the LocalModelChatbot with a specified model.
        
        Args:
            model_path (Optional[str]): Path to the local model directory. If None, uses default path.
            device (str): Device to load the model on ('cpu', 'cuda', or 'auto').
            load_in_8bit (bool): Whether to load the model in 8-bit precision to save memory.
            max_new_tokens (int): Maximum number of tokens to generate in responses.
            temperature (float): Sampling temperature for generation.
            top_k (int): Number of highest probability tokens to keep for top-k sampling.
            top_p (float): Cumulative probability threshold for top-p sampling.
            repetition_penalty (float): Penalty for repeating tokens.
        """
        # Set default model path if not provided
        if model_path is None:
            model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'finetunedmodel-merged'))
        
        self.model_path = model_path
        self.device = device
        self.load_in_8bit = load_in_8bit
        
        # Generation parameters
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p
        self.repetition_penalty = repetition_penalty
        
        # Load model and tokenizer
        self._load_model()
    
    def _load_model(self):
        """Load the model and tokenizer from the specified path."""
        try:
            logger.info(f"Loading model from: {self.model_path}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                load_in_8bit=self.load_in_8bit,
                device_map=self.device
            )
            
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def generate_response(self, user_message: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response to the user's message.
        
        Args:
            user_message (str): The user's input message.
            system_prompt (Optional[str]): Optional system prompt to guide the model's behavior.
                                          If None, a default prompt is used.
        
        Returns:
            str: The generated response.
        """
        # Use default system prompt if none provided
        if system_prompt is None:
            system_prompt = (
                "You are an AI assistant for a hotel. "
                "Be helpful, concise, and professional in your responses. "
                "If you don't know something, say so rather than making up information."
            )
        
        # Format the prompt for the model
        full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{user_message}\n<|assistant|>\n"
        
        try:
            # Tokenize the prompt
            inputs = self.tokenizer(full_prompt, return_tensors="pt", truncation=True, max_length=1024)
            inputs = {key: value.to(self.model.device) for key, value in inputs.items()}
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_new_tokens,
                    temperature=self.temperature,
                    top_k=self.top_k,
                    top_p=self.top_p,
                    repetition_penalty=self.repetition_penalty,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode the response
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract just the assistant's part of the response
            if "<|assistant|>" in full_response:
                assistant_response = full_response.split("<|assistant|>")[-1].strip()
                return assistant_response
            else:
                return full_response
        
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I'm sorry, I encountered an error: {str(e)}"
    
    def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a chat message and return a structured response.
        
        Args:
            message (str): The user's message.
            context (Optional[Dict[str, Any]]): Optional context information for the chat.
        
        Returns:
            Dict[str, Any]: A structured response containing the generated text and metadata.
        """
        try:
            # Generate the response
            response_text = self.generate_response(message)
            
            # Create a structured response
            response = {
                "text": response_text,
                "status": "success",
                "metadata": {
                    "model": os.path.basename(self.model_path),
                    "timestamp": None  # This would typically be filled with the current timestamp
                }
            }
            
            return response
        
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return {
                "text": f"I'm sorry, I encountered an error: {str(e)}",
                "status": "error",
                "error": str(e)
            }


# Example usage
if __name__ == "__main__":
    # Initialize the chatbot
    chatbot = LocalModelChatbot()
    
    # Example interaction
    user_input = "Hello, can you help me with room service?"
    response = chatbot.chat(user_input)
    
    print(f"User: {user_input}")
    print(f"Bot: {response['text']}")