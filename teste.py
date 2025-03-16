import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_model():
    """Load the local model from the correct snapshot directory"""
    model_path = "finetunedmodel-merged"

    print(f"Loading model from: {model_path}")

    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        trust_remote_code=True,
        load_in_8bit=True,  # Enable bitsandbytes quantization if needed
        device_map="auto"  # Automatically selects CUDA if available
    )

    print("✅ Model loaded successfully!")
    return model, tokenizer


def chat_with_model(model, tokenizer):
    """Chat with the model in the terminal"""
    print("\nWelcome to the chatbot! Type 'exit' to quit.")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            break

        # ✅ Add system prompt to enforce assistant behavior
        system_prompt = (
            "You are an AI assistant for a hotel. "
            "Respond to guests politely and efficiently. "
            "Keep responses concise and professional."
        )

        # ✅ Format the input with system prompt
        full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{user_input}\n<|assistant|>\n"

        # Tokenize and move input tensors to the correct device
        inputs = tokenizer(full_prompt, return_tensors="pt")
        inputs = {key: value.to(device) for key, value in inputs.items()}  

        # ✅ Generate response with sampling controls
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
        print("\n🤖 Chatbot:", response)


if __name__ == "__main__":
    model, tokenizer = load_model()
    chat_with_model(model, tokenizer)