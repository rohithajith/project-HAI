#!/usr/bin/env python
"""
Test script to check GPU availability and test the local GPT-2 model.
This script will:
1. Check if PyTorch is installed
2. Check if CUDA (GPU) is available
3. Display GPU information if available
4. Test loading the GPT-2 model
5. Generate a sample response

Usage:
    python test_gpu_and_model.py
"""

import sys
import os
import time

def check_pytorch():
    """Check if PyTorch is installed and CUDA is available"""
    print("Checking PyTorch installation...")
    
    try:
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        
        # Check CUDA availability
        cuda_available = torch.cuda.is_available()
        print(f"✅ CUDA available: {cuda_available}")
        
        if cuda_available:
            # Get GPU information
            device_count = torch.cuda.device_count()
            print(f"✅ GPU count: {device_count}")
            
            for i in range(device_count):
                print(f"✅ GPU {i}: {torch.cuda.get_device_name(i)}")
                props = torch.cuda.get_device_properties(i)
                print(f"   - Total memory: {props.total_memory / 1024 / 1024 / 1024:.2f} GB")
                print(f"   - CUDA capability: {props.major}.{props.minor}")
        else:
            print("ℹ️ No GPU detected. The model will run on CPU, which may be slower.")
        
        return True
    except ImportError:
        print("❌ PyTorch is not installed. Please install it with:")
        print("   pip install torch")
        return False

def check_transformers():
    """Check if Transformers is installed"""
    print("\nChecking Transformers installation...")
    
    try:
        import transformers
        print(f"✅ Transformers version: {transformers.__version__}")
        return True
    except ImportError:
        print("❌ Transformers is not installed. Please install it with:")
        print("   pip install transformers")
        return False

def test_model_loading():
    """Test loading the GPT-2 model"""
    print("\nTesting model loading...")
    
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        
        # Start timer
        start_time = time.time()
        
        # Set device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"ℹ️ Using device: {device}")
        
        # Create models directory if it doesn't exist
        model_dir = os.path.join("backend", "models")
        os.makedirs(model_dir, exist_ok=True)
        
        # Load tokenizer and model
        print("ℹ️ Loading GPT-2 tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained("gpt2", cache_dir=model_dir)
        
        print("ℹ️ Loading GPT-2 model (this may take a minute)...")
        model = AutoModelForCausalLM.from_pretrained("gpt2", cache_dir=model_dir)
        
        # Move model to device
        model = model.to(device)
        
        # End timer
        end_time = time.time()
        
        print(f"✅ Model loaded successfully in {end_time - start_time:.2f} seconds")
        
        return model, tokenizer, device
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None, None, None

def test_generation(model, tokenizer, device):
    """Test generating text with the model"""
    if model is None or tokenizer is None:
        return False
    
    print("\nTesting text generation...")
    
    try:
        # Prepare input
        prompt = "Welcome to our hotel! How can I assist you today?"
        print(f"ℹ️ Prompt: '{prompt}'")
        
        # Tokenize
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        
        # Start timer
        start_time = time.time()
        
        # Generate
        print("ℹ️ Generating response...")
        with torch.no_grad():
            output = model.generate(
                inputs["input_ids"],
                max_new_tokens=50,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode
        generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
        
        # End timer
        end_time = time.time()
        
        print(f"✅ Text generated in {end_time - start_time:.2f} seconds")
        print(f"ℹ️ Generated text: '{generated_text}'")
        
        return True
    except Exception as e:
        print(f"❌ Error generating text: {e}")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("GPU and Model Test")
    print("=" * 50)
    
    # Check PyTorch
    pytorch_ok = check_pytorch()
    if not pytorch_ok:
        return
    
    # Check Transformers
    transformers_ok = check_transformers()
    if not transformers_ok:
        return
    
    # Test model loading
    model, tokenizer, device = test_model_loading()
    if model is None:
        return
    
    # Test generation
    generation_ok = test_generation(model, tokenizer, device)
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"PyTorch: {'✅ Installed' if pytorch_ok else '❌ Not installed'}")
    print(f"Transformers: {'✅ Installed' if transformers_ok else '❌ Not installed'}")
    print(f"Model loading: {'✅ Successful' if model is not None else '❌ Failed'}")
    print(f"Text generation: {'✅ Successful' if generation_ok else '❌ Failed'}")
    
    if pytorch_ok and transformers_ok and model is not None and generation_ok:
        print("\n✅ All tests passed! The local model is ready to use.")
        print("You can now use the chatbot with the local model.")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()