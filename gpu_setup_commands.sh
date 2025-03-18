#!/bin/bash
# GPU Setup Commands for PyTorch and bitsandbytes
# This script provides commands to properly set up PyTorch with CUDA support and bitsandbytes

# 1. First, check CUDA availability and version
echo "Checking CUDA installation..."
nvidia-smi

# 2. Activate your Python environment (if using conda or virtualenv)
# Uncomment the appropriate line:
# conda activate myenv
# source myenv/bin/activate

# 3. Uninstall existing PyTorch and bitsandbytes
echo "Removing existing PyTorch and bitsandbytes installations..."
pip uninstall -y torch torchvision torchaudio bitsandbytes

# 4. Install PyTorch with CUDA support
# Choose the appropriate command based on your CUDA version:

# For CUDA 11.8
echo "Installing PyTorch with CUDA 11.8 support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 5. Verify PyTorch CUDA installation
echo "Verifying PyTorch CUDA installation..."
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda); print('GPU device count:', torch.cuda.device_count()); print('Current device:', torch.cuda.current_device()); print('Device name:', torch.cuda.get_device_name(0))"

# 6. Install bitsandbytes with CUDA support
echo "Installing bitsandbytes with CUDA support..."
pip install bitsandbytes

# 7. Verify bitsandbytes installation
echo "Verifying bitsandbytes installation..."
python -c "import bitsandbytes; print('bitsandbytes version:', bitsandbytes.__version__); from bitsandbytes.cuda_setup.main import get_compute_capabilities; print('CUDA capabilities:', get_compute_capabilities())"

# 8. Install other required packages
echo "Installing other required packages..."
pip install transformers accelerate

# 9. Test loading a model with 4-bit quantization
echo "Testing model loading with 4-bit quantization..."
python -c "
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

# Configure 4-bit quantization
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type='nf4'
)

# Load a small model to test
print('Loading model with 4-bit quantization...')
model_id = 'gpt2'  # Small model for testing
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map='auto',
    quantization_config=quantization_config
)
print('Model loaded successfully with 4-bit quantization')
"

echo "Setup complete! If all steps were successful, your GPU should now be properly configured for PyTorch and bitsandbytes."