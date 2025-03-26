"""
Model utility functions for the AI agents system
"""

import json
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("model_utils")

# System prompt for the hotel AI assistant
SYSTEM_PROMPT = """You are a helpful hotel AI assistant capable of both answering questions and processing requests. \
When guests make specific requests (like asking for towels), you should: \
1. Confirm the request with the guest \
2. Log the request in the admin dashboard \
3. Provide an estimated timeframe \
4. Continue being friendly and helpful"""

def load_model_and_tokenizer(model_path, cache_dir):
    """Load the model and tokenizer from local directory"""
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading model on {device} from: {model_path}")

        # Convert to forward-slash path for Hugging Face compatibility
        model_path = Path(model_path).resolve().as_posix()
        cache_dir = Path(cache_dir).resolve().as_posix()

        tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=model_path,
            cache_dir=cache_dir,
            local_files_only=True
        )
        model = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=model_path,
            cache_dir=cache_dir,
            local_files_only=True,
            torch_dtype=torch.float16 if device == "cuda" else None,
            device_map="auto" if device == "cuda" else None
        )

        return model, tokenizer, device

    except Exception as e:
        logger.error(f"Error loading model and tokenizer: {e}")
        raise

def format_prompt(message, history_json=None):
    """Format the conversation prompt"""
    try:
        history = json.loads(history_json) if history_json else []
    except json.JSONDecodeError:
        history = []

    prompt = f"{SYSTEM_PROMPT}\n\n"
    for msg in history:
        role = "Hotel AI" if msg["role"] == "system" else "User"
        prompt += f"{role}: {msg['content']}\n"
    prompt += f"User: {message}\nHotel AI:"

    return prompt

def generate_response(model, tokenizer, prompt, device):
    """Generate a response from the model"""
    try:
        import torch
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        output = model.generate(
            inputs["input_ids"],
            max_new_tokens=100,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        response = tokenizer.decode(output[0], skip_special_tokens=True)
        return response[len(prompt):].strip()
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        raise