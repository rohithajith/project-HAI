#!/usr/bin/env python
"""
Terminal-based chatbot script.
This script loads the local model and allows the user to chat with it in the terminal.
"""

import subprocess
import sys
import os
import json
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_model():
    """Load the local model"""
    model_name = "rohith0990/finetunedmodel-merged"
    print(f"Loading model: {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    print("✅ Model loaded successfully")
    return model, tokenizer

def chat_with_model(model, tokenizer):
    """Chat with the model in the terminal"""
    print("\nWelcome to the chatbot! Type 'exit' to quit.")
    history = []

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        # Add user input to history
        history.append({"role": "user", "content": user_input})

        # Prepare input for the model
        input_text = "\n".join([f"{item['role']}: {item['content']}" for item in history])
        inputs = tokenizer(input_text, return_tensors="pt")

        # Generate response
        outputs = model.generate(**inputs, max_length=150, num_return_sequences=1)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract the new response from the full output
        new_response = response.split(f"user: {user_input}")[-1].strip()

        # Add response to history
        history.append({"role": "assistant", "content": new_response})

        print(f"Chatbot: {new_response}")

if __name__ == "__main__":
    model, tokenizer = load_model()
    chat_with_model(model, tokenizer)