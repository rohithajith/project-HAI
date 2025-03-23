"""
Test script for the local quantized model.

This script tests the model loading and generation capabilities without the full agent flow.
"""

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

def get_model_path():
    """Get the absolute path to the model directory."""
    # Get the current script directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the project root (two levels up from the current script)
    project_root = os.path.dirname(os.path.dirname(current_dir))
    # Return the path to the model directory
    return os.path.join(project_root, "finetunedmodel-merged")

def load_model():
    """Load the local model from the correct snapshot directory."""
    model_path = get_model_path()
    
    print(f"Loading model from: {model_path}")
    
    # Configure 8-bit quantization
    quantization_config = BitsAndBytesConfig(
        load_in_8bit=True,
        llm_int8_enable_fp32_cpu_offload=True
    )
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        trust_remote_code=True,
        local_files_only=True  # Explicitly use local files only
    )
    
    # Load model with quantization and CUDA support
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        trust_remote_code=True,
        local_files_only=True,  # Explicitly use local files only
        quantization_config=quantization_config,  # Use BitsAndBytesConfig instead of load_in_8bit
        device_map="auto"       # Automatically use CUDA if available
    )
    
    print("✅ Model loaded successfully!")
    return model, tokenizer

def chat_with_model(model, tokenizer):
    """Test the model with a preset query."""
    print("\nTesting model with preset queries...")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Test queries for different agent types
    test_queries = [
        {
            "type": "Check-in",
            "query": "I'd like to check in to my room. My booking ID is BK12345."
        },
        {
            "type": "Room Service",
            "query": "Can I get some extra towels and pillows delivered to room 301?"
        },
        {
            "type": "Wellness",
            "query": "I'd like to do a guided meditation session."
        }
    ]
    
    for test in test_queries:
        print(f"\n\n--- Testing {test['type']} Query ---")
        print(f"Query: {test['query']}")
        
        # Add system prompt to enforce assistant behavior
        system_prompt = (
            "You are an AI assistant for a hotel. "
            "Respond to guests politely and efficiently. "
            "Keep responses concise and professional."
        )
        
        # Format the input with system prompt
        full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{test['query']}\n<|assistant|>\n"
        
        # Tokenize and move input tensors to the correct device
        inputs = tokenizer(full_prompt, return_tensors="pt")
        inputs = {key: value.to(device) for key, value in inputs.items()}
        
        print("Generating response...")
        
        # Generate response with sampling controls
        outputs = model.generate(
            **inputs,
            max_length=150,
            temperature=0.7,  # Controls randomness (lower = more predictable)
            top_k=50,         # Limits low-likelihood words
            top_p=0.9,        # Nucleus sampling (removes unlikely words)
            repetition_penalty=1.2  # Reduces repeating phrases
        )
        
        # Decode and print the response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print("\nResponse:")
        print(response)

def main():
    """Run the test script."""
    print("=" * 50)
    print("TESTING LOCAL QUANTIZED MODEL")
    print("=" * 50)
    
    try:
        # Load the model and tokenizer
        model, tokenizer = load_model()
        
        # Test the model with preset queries
        chat_with_model(model, tokenizer)
        
        print("\n" + "=" * 50)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 50)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 50)
        print("TEST FAILED")
        print("=" * 50)

if __name__ == "__main__":
    main()