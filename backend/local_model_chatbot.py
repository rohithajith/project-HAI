#!/usr/bin/env python
"""
Local Model Chatbot Script for Hotel Management System

This script uses a locally downloaded model (GPT-2) to generate responses
for the hotel chatbot. It downloads the model if it doesn't exist locally,
and provides an interface similar to the original chatbot_bridge.py.

Usage:
    python local_model_chatbot.py --message "User message" [--history "JSON history string"]

Requirements:
    - torch
    - transformers
"""

import argparse
import json
import os
import sys
import logging
from pathlib import Path

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
MODEL_NAME = "models/rohith0990_finetunedmodel_merged/"  # Using the downloaded fine-tuned model
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

def load_model_and_tokenizer():
    """Load the model and tokenizer, downloading if necessary"""
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        
        # Check if we have GPU info
        if device == "cuda":
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024 / 1024 / 1024:.2f} GB")
        
        # Load tokenizer and model (will download if not present)
        logger.info(f"Loading model and tokenizer from {MODEL_NAME}")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=MODEL_DIR)
        model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, cache_dir=MODEL_DIR)
        
        # Move model to device (GPU if available)
        model = model.to(device)
        
        return model, tokenizer, device
    except ImportError as e:
        logger.error(f"Error importing required modules: {e}")
        logger.error("Please install the required packages with: pip install torch transformers")
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
    
    return prompt

def generate_response(model, tokenizer, prompt, device):
    """Generate a response using the local model"""
    try:
        import torch
        
        # Tokenize the prompt
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        
        # Generate a response
        with torch.no_grad():
            output = model.generate(
                inputs["input_ids"],
                max_new_tokens=100,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
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
        
        return response
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return "I apologize, but I couldn't process your request at the moment."

def process_message(message, history_json=None):
    """Process a message and return a response"""
    try:
        # Load the model and tokenizer
        model, tokenizer, device = load_model_and_tokenizer()
        
        # Format the prompt
        prompt = format_prompt(message, history_json)
        
        # Generate a response
        response = generate_response(model, tokenizer, prompt, device)
        
        return {"response": response}
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