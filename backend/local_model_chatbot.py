#!/usr/bin/env python
"""
Local Model Chatbot Script for Hotel Management System
"""

import argparse
import json
import logging
from .model_utils import load_model_and_tokenizer, format_prompt, generate_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("local_model_chatbot")

def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(description="Local model chatbot for hotel management system")
    parser.add_argument("--message", required=True, help="User message")
    parser.add_argument("--history", help="JSON string of conversation history")
    
    args = parser.parse_args()
    
    try:
        # Load model
        model, tokenizer, device = load_model_and_tokenizer(
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "finetunedmodel-merged"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        )
        
        # Generate response
        prompt = format_prompt(args.message, args.history)
        response = generate_response(model, tokenizer, prompt, device)
        
        print(json.dumps({
            "response": response,
            "serviceRequest": False
        }))
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        print(json.dumps({
            "response": "I apologize, but I couldn't process your request at the moment.",
            "serviceRequest": False
        }))

if __name__ == "__main__":
    main()