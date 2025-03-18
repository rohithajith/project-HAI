#!/usr/bin/env python
"""
Local Model Chatbot Script for Hotel Management System with Metrics Collection

This script uses a locally downloaded model (GPT-2) to generate responses
for the hotel chatbot. It downloads the model if it doesn't exist locally,
and provides an interface similar to the original chatbot_bridge.py.
It also collects and returns metrics about token usage and latency.

Usage:
    python local_model_chatbot_metrics.py --message "User message" [--history "JSON history string"]

Requirements:
    - torch
    - transformers
"""

import argparse
import json
import os
import sys
import logging
import time
from pathlib import Path
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("local_model_chatbot")

# System prompt for the hotel AI assistant
SYSTEM_PROMPT = "you are a helpfull hotel ai which acts like hotel reception udating requests and handiling queries from users"

# Model configuration
MODEL_NAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "finetunedmodel-merged")  # Using the downloaded fine-tuned model
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

# Helper functions for model loading strategies
def load_with_bitsandbytes_4bit(model_name, cache_dir):
    """Load model with 4-bit quantization using bitsandbytes"""
    from transformers import AutoModelForCausalLM, BitsAndBytesConfig
    import torch
    import bitsandbytes as bnb
    
    # Configure 4-bit quantization
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )
    
    # Load model with quantization
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        cache_dir=cache_dir,
        device_map="auto",
        quantization_config=quantization_config
    )
    
    return model

def load_with_bitsandbytes_8bit(model_name, cache_dir):
    """Load model with 8-bit quantization using bitsandbytes"""
    from transformers import AutoModelForCausalLM, BitsAndBytesConfig
    import torch
    import bitsandbytes as bnb
    
    # Configure 8-bit quantization
    quantization_config = BitsAndBytesConfig(
        load_in_8bit=True,
        llm_int8_threshold=6.0
    )
    
    # Load model with quantization
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        cache_dir=cache_dir,
        device_map="auto",
        quantization_config=quantization_config
    )
    
    return model

def load_with_fp16(model_name, cache_dir):
    """Load model with FP16 precision"""
    from transformers import AutoModelForCausalLM
    import torch
    
    # Load with half precision
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        cache_dir=cache_dir,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    return model

def load_standard(model_name, cache_dir, device):
    """Load model with standard settings"""
    from transformers import AutoModelForCausalLM
    
    # Standard loading
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        cache_dir=cache_dir,
        low_cpu_mem_usage=True
    )
    
    # Move model to device
    model = model.to(device)
    
    return model

# PII patterns for detection
PII_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
    'credit_card': r'\b(?:\d{4}[- ]?){3}\d{4}\b',
    'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
    'address': r'\b\d+\s+[A-Za-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Court|Ct|Lane|Ln|Way|Parkway|Pkwy)\b',
}

def detect_pii(text):
    """Detect PII in text and return a list of matches"""
    pii_found = []
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            pii_found.append({
                'type': pii_type,
                'value': match.group(),
                'start': match.start(),
                'end': match.end()
            })
    return pii_found

def load_model_and_tokenizer():
    """Load the model and tokenizer, downloading if necessary"""
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        
        start_time = time.time()

        # Check if CUDA is available
        if not torch.cuda.is_available():
            logger.warning("CUDA not available. This script is optimized for GPU usage.")
            device = "cpu"
            
            # CPU loading - simple path to avoid bitsandbytes completely
            logger.info("Loading model on CPU")
            logger.info(f"Loading tokenizer from {MODEL_NAME}")
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=MODEL_DIR)
            
            # Standard loading for CPU
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                cache_dir=MODEL_DIR,
                low_cpu_mem_usage=True
            )
            model = model.to(device)
        else:
            # GPU path
            device = "cuda"
            logger.info(f"Using device: {device}")
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024 / 1024 / 1024:.2f} GB")
            logger.info(f"CUDA Version: {torch.version.cuda}")
            
            # Import GPU-specific modules only when CUDA is available
            from transformers import BitsAndBytesConfig
            
            # Load tokenizer
            logger.info(f"Loading tokenizer from {MODEL_NAME}")
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=MODEL_DIR)
            
            # Configure model loading for GPU
            logger.info("Checking CUDA setup...")
            
            # Check CUDA version and capabilities
            cuda_version = torch.version.cuda
            logger.info(f"CUDA Version from PyTorch: {cuda_version}")
            
            # Try different loading strategies in order of preference
            loading_strategies = [
                {
                    "name": "4-bit quantization with bitsandbytes",
                    "fn": lambda: load_with_bitsandbytes_4bit(MODEL_NAME, MODEL_DIR)
                },
                {
                    "name": "8-bit quantization with bitsandbytes",
                    "fn": lambda: load_with_bitsandbytes_8bit(MODEL_NAME, MODEL_DIR)
                },
                {
                    "name": "FP16 precision",
                    "fn": lambda: load_with_fp16(MODEL_NAME, MODEL_DIR)
                },
                {
                    "name": "Standard loading with GPU",
                    "fn": lambda: load_standard(MODEL_NAME, MODEL_DIR, device)
                }
            ]
            
            # Try each strategy until one works
            model = None
            for strategy in loading_strategies:
                try:
                    logger.info(f"Trying to load model with {strategy['name']}...")
                    model = strategy["fn"]()
                    logger.info(f"Successfully loaded model with {strategy['name']}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load with {strategy['name']}: {e}")
            
            # If all strategies failed, raise an error
            if model is None:
                raise RuntimeError("All GPU loading strategies failed. Check your CUDA setup.")
        
        load_time = time.time() - start_time
        logger.info(f"Model loaded in {load_time:.2f} seconds")
        
        return model, tokenizer, device, load_time
    except ImportError as e:
        logger.error(f"Error importing required modules: {e}")
        logger.error("Please install the required packages with: pip install torch transformers bitsandbytes")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        sys.exit(1)

def format_prompt(message, history_json=None):
    """Format the conversation history into a prompt for the model"""
    try:
        history = json.loads(history_json) if history_json else []
    except json.JSONDecodeError:
        logger.error("Error: Invalid JSON history format")
        history = []
    
    # Create a simple prompt with system message and conversation history
    prompt = f"{SYSTEM_PROMPT}\n\n"
    
    for msg in history:
        role = "Hotel AI" if msg["role"] == "system" else ("User" if msg["role"] == "user" else "Hotel AI")
        prompt += f"{role}: {msg['content']}\n"
    
    prompt += f"User: {message}\nHotel AI:"
    
    return prompt, history

def generate_response(model, tokenizer, prompt, device):
    """Generate a response using the local model and collect metrics"""
    try:
        import torch
        
        metrics = {
            "model_name": MODEL_NAME,
            "device": device,
            "tokens_input": 0,
            "tokens_output": 0,
            "generation_time": 0
        }
        
        # Tokenize the prompt
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        metrics["tokens_input"] = len(inputs["input_ids"][0])
        
        # Generate a response
        start_time = time.time()
        with torch.no_grad():
            output = model.generate(
                inputs["input_ids"],
                max_new_tokens=100,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        generation_time = time.time() - start_time
        metrics["generation_time"] = generation_time
        
        # Calculate output tokens
        metrics["tokens_output"] = len(output[0]) - len(inputs["input_ids"][0])
        
        # Decode the response
        response = tokenizer.decode(output[0], skip_special_tokens=True)
        
        # Extract just the model's response (after the prompt)
        response = response[len(prompt):].strip()
        
        # Clean up the response
        if "User:" in response:
            response = response.split("User:")[0].strip()
        
        if "Hotel AI:" in response:
            response = response.split("Hotel AI:")[0].strip()
        
        # If the response is too short or empty, provide a default response
        if not response or len(response) < 10:
            response = "Welcome to our hotel! How can I assist you today?"
        
        # Detect PII in the response
        pii_found = detect_pii(response)
        if pii_found:
            logger.warning(f"PII detected in response: {pii_found}")
            metrics["pii_detected"] = True
            
            # Redact PII in the response
            for pii in sorted(pii_found, key=lambda x: x["start"], reverse=True):
                response = response[:pii["start"]] + f"[REDACTED {pii['type']}]" + response[pii["end"]:]
        
        return response, metrics
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return "I apologize, but I couldn't process your request at the moment.", {
            "error": str(e),
            "model_name": MODEL_NAME,
            "device": device
        }

def process_message(message, history_json=None):
    """Process a message and return a response with metrics"""
    try:
        start_time = time.time()
        
        # Load the model and tokenizer
        model, tokenizer, device, load_time = load_model_and_tokenizer()
        
        # Format the prompt
        prompt, history = format_prompt(message, history_json)
        
        # Generate a response
        response, metrics = generate_response(model, tokenizer, prompt, device)
        
        # Add additional metrics
        metrics["total_time"] = time.time() - start_time
        metrics["load_time"] = load_time
        metrics["prompt_length"] = len(prompt)
        metrics["response_length"] = len(response)
        
        # Detect PII in the user message
        pii_in_message = detect_pii(message)
        if pii_in_message:
            logger.warning(f"PII detected in user message: {pii_in_message}")
            metrics["pii_in_message"] = True
        
        return {
            "response": response,
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return {"error": f"Error processing message: {str(e)}"}

def main():
    """Main function to parse arguments and process the message"""
    parser = argparse.ArgumentParser(description="Local model chatbot for hotel management system")
    parser.add_argument("--message", required=True, help="User message")
    parser.add_argument("--history", help="JSON string of conversation history")
    
    args = parser.parse_args()
    
    result = process_message(args.message, args.history)
    print(json.dumps(result))

if __name__ == "__main__":
    main()