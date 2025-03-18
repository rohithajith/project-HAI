# GPU Setup Guide for PyTorch and bitsandbytes

This guide provides detailed instructions for setting up PyTorch with CUDA support and bitsandbytes for GPU acceleration, which is required for running quantized language models efficiently.

## Prerequisites

- NVIDIA GPU with CUDA support
- NVIDIA drivers installed
- CUDA Toolkit installed (version 11.8 or 12.1 recommended)
- Python environment (conda or virtualenv recommended)

## Step 1: Check CUDA Installation

First, verify that your NVIDIA GPU is properly recognized and CUDA is available:

```bash
nvidia-smi
```

This should display information about your GPU, including the CUDA version. Make note of this version for later steps.

## Step 2: Set Up Python Environment

It's recommended to use a dedicated Python environment:

### Using conda:
```bash
conda create -n llm-env python=3.10
conda activate llm-env
```

### Using virtualenv:
```bash
python -m venv llm-env
# On Windows:
llm-env\Scripts\activate
# On Linux/Mac:
source llm-env/bin/activate
```

## Step 3: Install PyTorch with CUDA Support

Uninstall any existing PyTorch installations:

```bash
pip uninstall -y torch torchvision torchaudio
```

Install PyTorch with the appropriate CUDA version:

### For CUDA 11.8:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### For CUDA 12.1:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## Step 4: Verify PyTorch CUDA Installation

Run the following Python code to verify that PyTorch can access your GPU:

```python
import torch
print("CUDA available:", torch.cuda.is_available())
print("CUDA version:", torch.version.cuda)
print("GPU device count:", torch.cuda.device_count())
print("Current device:", torch.cuda.current_device())
print("Device name:", torch.cuda.get_device_name(0))
```

All of these should return valid information about your GPU. If `torch.cuda.is_available()` returns `False`, there's an issue with your CUDA setup.

## Step 5: Install bitsandbytes

### On Linux/Mac:
```bash
pip install bitsandbytes
```

### On Windows:
Windows support for bitsandbytes is more complex. Try these options in order:

1. Install the Windows-specific version:
   ```bash
   pip install bitsandbytes-windows
   ```

2. If that doesn't work, try the standard version:
   ```bash
   pip install bitsandbytes
   ```

3. If both fail, you may need to compile from source:
   ```bash
   git clone https://github.com/Keith-Hon/bitsandbytes-windows.git
   cd bitsandbytes-windows
   pip install -e .
   ```

## Step 6: Verify bitsandbytes Installation

Run the following Python code to verify that bitsandbytes is properly installed:

```python
import bitsandbytes
print("bitsandbytes version:", bitsandbytes.__version__)

# On Linux/Mac, you can also check CUDA capabilities:
from bitsandbytes.cuda_setup.main import get_compute_capabilities
print("CUDA capabilities:", get_compute_capabilities())
```

## Step 7: Install Other Required Packages

```bash
pip install transformers accelerate
```

## Step 8: Test Loading a Model with Quantization

Run the following Python code to test loading a model with 4-bit quantization:

```python
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
```

If this runs without errors, your setup is working correctly.

## Troubleshooting

### CUDA Not Available

If `torch.cuda.is_available()` returns `False`:

1. Check that your NVIDIA drivers are installed and up to date
2. Verify that the CUDA Toolkit is installed
3. Make sure you installed the correct PyTorch version for your CUDA version
4. Check that your GPU is supported by the installed CUDA version

### bitsandbytes Installation Issues

#### Windows-Specific Issues:

1. Make sure you have the Visual C++ Redistributable installed
2. Try the Windows-specific fork: `pip install bitsandbytes-windows`
3. Check the [bitsandbytes Windows issue thread](https://github.com/TimDettmers/bitsandbytes/issues/156) for the latest solutions

#### Linux-Specific Issues:

1. Make sure you have the correct CUDA libraries in your path
2. Try installing with: `pip install bitsandbytes --no-cache-dir`

### Model Loading Issues

If you encounter errors when loading models with quantization:

1. Start with a small model like 'gpt2' to test the basic functionality
2. Check that you have enough GPU memory for the model you're trying to load
3. Try different quantization settings (8-bit instead of 4-bit)
4. Update to the latest versions of transformers and accelerate

## Additional Resources

- [PyTorch Installation Guide](https://pytorch.org/get-started/locally/)
- [bitsandbytes GitHub Repository](https://github.com/TimDettmers/bitsandbytes)
- [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers/index)
- [NVIDIA CUDA Installation Guide](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/index.html)

## Using with Our Project

After setting up your environment, you can run our local_model_chatbot_metrics.py script with:

```bash
python backend/local_model_chatbot_metrics.py --message "Your message here"
```

The script will automatically detect your GPU and use the appropriate loading strategy for the model.