#!/usr/bin/env python
"""
GPU Setup Test Script

This script tests if your GPU setup is working correctly for PyTorch and bitsandbytes.
It checks CUDA availability, tests loading a model with quantization, and runs a simple inference.

Usage:
    python test_gpu_setup.py
"""

import os
import sys
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("gpu_test")

def check_cuda():
    """Check if CUDA is available and print GPU information"""
    logger.info("Checking CUDA availability...")
    
    try:
        import torch
        
        cuda_available = torch.cuda.is_available()
        logger.info(f"CUDA available: {cuda_available}")
        
        if cuda_available:
            logger.info(f"CUDA version: {torch.version.cuda}")
            logger.info(f"GPU device count: {torch.cuda.device_count()}")
            logger.info(f"Current device: {torch.cuda.current_device()}")
            logger.info(f"Device name: {torch.cuda.get_device_name(0)}")
            
            # Get GPU memory information
            device = torch.cuda.current_device()
            gpu_properties = torch.cuda.get_device_properties(device)
            logger.info(f"Total memory: {gpu_properties.total_memory / 1024 / 1024 / 1024:.2f} GB")
            
            return True
        else:
            logger.error("CUDA is not available. Check your PyTorch installation and GPU drivers.")
            return False
    except ImportError:
        logger.error("PyTorch is not installed. Install it with CUDA support.")
        return False
    except Exception as e:
        logger.error(f"Error checking CUDA: {e}")
        return False

def check_bitsandbytes():
    """Check if bitsandbytes is installed and working"""
    logger.info("Checking bitsandbytes installation...")
    
    try:
        import bitsandbytes as bnb
        
        logger.info(f"bitsandbytes version: {bnb.__version__}")
        
        # Try to get CUDA capabilities (Linux/Mac only)
        try:
            from bitsandbytes.cuda_setup.main import get_compute_capabilities
            logger.info(f"CUDA capabilities: {get_compute_capabilities()}")
        except:
            logger.info("Could not get CUDA capabilities (this is normal on Windows)")
        
        return True
    except ImportError:
        logger.error("bitsandbytes is not installed. Install it with: pip install bitsandbytes")
        return False
    except Exception as e:
        logger.error(f"Error checking bitsandbytes: {e}")
        return False

def test_model_loading():
    """Test loading a model with quantization"""
    logger.info("Testing model loading with quantization...")
    
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        
        # Configure 4-bit quantization
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
        
        # Load a small model to test
        model_id = "gpt2"  # Small model for testing
        logger.info(f"Loading model {model_id} with 4-bit quantization...")
        
        start_time = time.time()
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            quantization_config=quantization_config
        )
        load_time = time.time() - start_time
        
        logger.info(f"Model loaded successfully in {load_time:.2f} seconds")
        
        # Test inference
        logger.info("Testing inference...")
        input_text = "Hello, I'm a language model"
        
        inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
        start_time = time.time()
        
        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                max_new_tokens=20,
                do_sample=True,
                temperature=0.7
            )
        
        inference_time = time.time() - start_time
        output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        logger.info(f"Inference completed in {inference_time:.2f} seconds")
        logger.info(f"Input: {input_text}")
        logger.info(f"Output: {output_text}")
        
        return True
    except ImportError as e:
        logger.error(f"Missing required packages: {e}")
        logger.error("Install required packages with: pip install transformers accelerate")
        return False
    except Exception as e:
        logger.error(f"Error testing model loading: {e}")
        return False

def test_8bit_loading():
    """Test loading a model with 8-bit quantization as a fallback"""
    logger.info("Testing model loading with 8-bit quantization (fallback)...")
    
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        
        # Configure 8-bit quantization
        quantization_config = BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_threshold=6.0
        )
        
        # Load a small model to test
        model_id = "gpt2"  # Small model for testing
        logger.info(f"Loading model {model_id} with 8-bit quantization...")
        
        start_time = time.time()
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            quantization_config=quantization_config
        )
        load_time = time.time() - start_time
        
        logger.info(f"Model loaded successfully in {load_time:.2f} seconds")
        return True
    except Exception as e:
        logger.error(f"Error testing 8-bit model loading: {e}")
        return False

def test_fp16_loading():
    """Test loading a model with FP16 precision as a fallback"""
    logger.info("Testing model loading with FP16 precision (fallback)...")
    
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        # Load a small model to test
        model_id = "gpt2"  # Small model for testing
        logger.info(f"Loading model {model_id} with FP16 precision...")
        
        start_time = time.time()
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        load_time = time.time() - start_time
        
        logger.info(f"Model loaded successfully in {load_time:.2f} seconds")
        return True
    except Exception as e:
        logger.error(f"Error testing FP16 model loading: {e}")
        return False

def main():
    """Main function to run all tests"""
    logger.info("Starting GPU setup test...")
    
    # Check CUDA
    cuda_ok = check_cuda()
    if not cuda_ok:
        logger.error("CUDA check failed. Please check your GPU setup.")
        return
    
    # Check bitsandbytes
    bnb_ok = check_bitsandbytes()
    if not bnb_ok:
        logger.warning("bitsandbytes check failed. Some tests may not work.")
    
    # Test model loading with 4-bit quantization
    model_ok = test_model_loading()
    
    # If 4-bit fails, try 8-bit
    if not model_ok:
        logger.warning("4-bit quantization failed, trying 8-bit...")
        model_ok = test_8bit_loading()
    
    # If 8-bit fails, try FP16
    if not model_ok:
        logger.warning("8-bit quantization failed, trying FP16...")
        model_ok = test_fp16_loading()
    
    # Summary
    logger.info("\n--- Test Summary ---")
    logger.info(f"CUDA available: {'✅' if cuda_ok else '❌'}")
    logger.info(f"bitsandbytes working: {'✅' if bnb_ok else '❌'}")
    logger.info(f"Model loading: {'✅' if model_ok else '❌'}")
    
    if cuda_ok and bnb_ok and model_ok:
        logger.info("All tests passed! Your GPU setup is working correctly.")
    else:
        logger.warning("Some tests failed. Check the logs for details.")

if __name__ == "__main__":
    main()