"""
Standalone test script for the Hotel AI Assistant.

This script tests the model loading and agent functionality without relying on the package structure.
"""

import os
import sys
import asyncio
import torch
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline
# Use the updated import for HuggingFacePipeline
from langchain_huggingface import HuggingFacePipeline
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms import HuggingFacePipeline
# Path to the model directory
MODEL_PATH = os.path.join(os.getcwd(), "finetunedmodel-merged")

def load_model():
    """Load the local model from the correct snapshot directory."""
    print(f"Loading model from: {MODEL_PATH}")
    
    # Configure 8-bit quantization
    quantization_config = BitsAndBytesConfig(
        load_in_8bit=True,
        llm_int8_enable_fp32_cpu_offload=True
    )
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_PATH,
        trust_remote_code=True,
        local_files_only=True  # Explicitly use local files only
    )
    
    # Load model with quantization and CUDA support
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        trust_remote_code=True,
        local_files_only=True,  # Explicitly use local files only
        quantization_config=quantization_config,  # Use BitsAndBytesConfig instead of load_in_8bit
        device_map="auto"       # Automatically use CUDA if available
    )
    
    print("✅ Model loaded successfully!")
    return model, tokenizer

def test_direct_model_generation(model, tokenizer):
    """Test the model with direct generation."""
    print("\n--- Testing Direct Model Generation ---")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Test queries
    test_queries = [
        "I'd like to check in to my room. My booking ID is BK12345.",
        "Can I get some extra towels and pillows delivered to room 301?",
        "I'd like to do a guided meditation session.",
        "When is check-in and check-out time?",
        "Where is the parking located?",
        "Is there an iron box in the room? Where can I find it?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        
        # Add system prompt to enforce assistant behavior
        system_prompt = (
            "You are an AI assistant for a hotel. "
            "Respond to guests politely and efficiently. "
            "Keep responses concise and professional."
        )
        
        # Format the input with system prompt
        full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{query}\n<|assistant|>\n"
        
        # Tokenize and move input tensors to the correct device
        inputs = tokenizer(full_prompt, return_tensors="pt")
        inputs = {key: value.to(device) for key, value in inputs.items()}
        
        print("Generating response...")
        
        # Generate response with sampling controls
        outputs = model.generate(
            **inputs,
            max_length=150,
            temperature=0.7,
            top_k=50,
            top_p=0.9,
            repetition_penalty=1.2
        )
        
        # Decode and print the response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Response: {response}")

def test_langchain_pipeline(model, tokenizer):
    """Test the model with LangChain pipeline."""
    print("\n--- Testing LangChain Pipeline ---")
    
    # Create a text generation pipeline
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=2000,
        temperature=0.7,
        top_p=0.9,
        top_k=50,
        repetition_penalty=1.2
    )
    
    # Create a LangChain wrapper around the pipeline
    llm = HuggingFacePipeline(pipeline=pipe)
    
    # Create the prompt template for check-in
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are a hotel check-in assistant. Your job is to help guests check in to the hotel.
        You need to verify their identity, confirm their booking details, and issue room keys.
        
        Be professional, courteous, and efficient. If there are any issues with the booking,
        try to resolve them or escalate to a human staff member if necessary.
        """),
        ("human", "{input}")
    ])
    
    # Test query
    query = "I'd like to check in to my room. My booking ID is BK12345."
    print(f"Query: {query}")
    
    # Format the input for the LLM
    formatted_input = f"""
    Booking ID: BK12345
    Guest Name: John Doe
    ID Verified: Yes
    Payment Verified: Yes
    
    Latest Message:
    {query}
    """
    
    print("Generating response...")
    
    # Format the prompt first
    formatted_prompt = prompt.format(input=formatted_input)
    
    # Then invoke the LLM with the formatted prompt
    llm_response = llm.invoke(formatted_prompt)
    
    # The response might be a string directly, not an object with a content attribute
    if hasattr(llm_response, 'content'):
        print(f"Response: {llm_response.content}")
    else:
        print(f"Response: {llm_response}")

def main():
    """Run the test script."""
    print("=" * 50)
    print("TESTING HOTEL AI ASSISTANT")
    print("=" * 50)
    
    # Load the model once
    print("Loading model for all tests...")
    model, tokenizer = load_model()
    
    # Test direct model generation
    test_direct_model_generation(model, tokenizer)
    
    # Test LangChain pipeline
    test_langchain_pipeline(model, tokenizer)
    
    print("\n" + "=" * 50)
    print("TEST COMPLETED SUCCESSFULLY")
    print("=" * 50)

if __name__ == "__main__":
    main()