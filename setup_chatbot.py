import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load the model and tokenizer
model_name = "finetunedmodel-merged"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name, 
    device_map="cpu", 
    load_in_8bit=False  # Disable 8-bit loading on non-CUDA machines
)

# Function to generate a response from the model
def generate_response(prompt, max_length=50):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=max_length)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Example usage
if __name__ == "__main__":
    prompt = "Hello, how can I assist you today?"
    response = generate_response(prompt)
    print("User:", prompt)
    print("Chatbot:", response)