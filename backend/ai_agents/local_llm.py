from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict
from langchain_core.language_models import LLM
from langchain_core.callbacks import CallbackManagerForLLMRun
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os

class LocalLLM(LLM, BaseModel):
    """
    A LangChain-compatible wrapper for a local fine-tuned model using Pydantic v2.
    
    Attributes:
        model_path (str): Path to the local model
        model (Any): Loaded transformer model
        tokenizer (Any): Tokenizer for the model
    """
    
    model_path: str = Field(
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'finetunedmodel-merged')),
        description="Path to the local model directory"
    )
    
    model: Any = Field(
        default=None, 
        exclude=True, 
        description="Loaded transformer model"
    )
    
    tokenizer: Any = Field(
        default=None, 
        exclude=True, 
        description="Model tokenizer"
    )
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True
    )
    
    def __init__(self, model=None, tokenizer=None, **data):
        """
        Initialize the LocalLLM, loading model if not provided.
        
        Args:
            model (Optional[AutoModelForCausalLM]): Pre-loaded model
            tokenizer (Optional[AutoTokenizer]): Pre-loaded tokenizer
            **data: Additional configuration data
        """
        # If model or tokenizer not provided, load from path
        if model is None or tokenizer is None:
            print(f"Loading model from: {self.model_path}")
            tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, 
                trust_remote_code=True
            )
            model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                load_in_8bit=True,
                device_map="auto"
            )
        
        # Update model and tokenizer
        data['model'] = model
        data['tokenizer'] = tokenizer
        
        # Call Pydantic's model initialization
        super().__init__(**data)
    
    @property
    def _llm_type(self) -> str:
        """
        Provide a type identifier for the LLM.
        
        Returns:
            str: Type of the local model
        """
        return "hotel_fine_tuned_model"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs
    ) -> str:
        """
        Generate a response using the local model.
        
        Args:
            prompt (str): Input prompt
            stop (Optional[List[str]]): Stop sequences
            run_manager (Optional[CallbackManagerForLLMRun]): Callback manager
            **kwargs: Additional generation parameters
        
        Returns:
            str: Generated response
        """
        # Prepare system and conversation context
        system_prompt = (
            "You are an AI assistant for a hotel. "
            "Respond to guests politely and efficiently. "
            "You have access to tools for room service, maintenance, booking, and more."
        )
        
        full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{prompt}\n<|assistant|>\n"
        
        # Tokenize and generate
        inputs = self.tokenizer(full_prompt, return_tensors="pt", truncation=True, max_length=1024)
        inputs = {key: value.to(self.model.device) for key, value in inputs.items()}
        
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
        
        # Decode and extract assistant's response
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        if "<|assistant|>" in full_response:
            assistant_response = full_response.split("<|assistant|>")[-1].strip()
            return assistant_response
        else:
            return full_response