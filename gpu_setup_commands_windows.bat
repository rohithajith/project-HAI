@echo off
REM GPU Setup Commands for PyTorch and bitsandbytes on Windows
REM This script provides commands to properly set up PyTorch with CUDA support and bitsandbytes

REM 1. First, check CUDA availability and version
echo Checking CUDA installation...
nvidia-smi

REM 2. Activate your Python environment (if using conda or virtualenv)
REM Uncomment the appropriate line:
REM call conda activate myenv
REM call myenv\Scripts\activate

REM 3. Uninstall existing PyTorch and bitsandbytes
echo Removing existing PyTorch and bitsandbytes installations...
pip uninstall -y torch torchvision torchaudio bitsandbytes

REM 4. Install PyTorch with CUDA support
REM Choose the appropriate command based on your CUDA version:

REM For CUDA 11.8
echo Installing PyTorch with CUDA 11.8 support...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

REM For CUDA 12.1
REM pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

REM 5. Verify PyTorch CUDA installation
echo Verifying PyTorch CUDA installation...
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda); print('GPU device count:', torch.cuda.device_count()); print('Current device:', torch.cuda.current_device()); print('Device name:', torch.cuda.get_device_name(0))"

REM 6. Install bitsandbytes with CUDA support
echo Installing bitsandbytes with CUDA support...

REM For Windows, we need to install a specific version of bitsandbytes that supports Windows
pip install bitsandbytes-windows

REM If the above doesn't work, try the standard version
REM pip install bitsandbytes

REM 7. Verify bitsandbytes installation
echo Verifying bitsandbytes installation...
python -c "import bitsandbytes; print('bitsandbytes version:', bitsandbytes.__version__)"

REM 8. Install other required packages
echo Installing other required packages...
pip install transformers accelerate

REM 9. Test loading a model with 4-bit quantization
echo Testing model loading with 4-bit quantization...
python -c "from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig; import torch; quantization_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True, bnb_4bit_quant_type='nf4'); print('Loading model with 4-bit quantization...'); model_id = 'gpt2'; tokenizer = AutoTokenizer.from_pretrained(model_id); model = AutoModelForCausalLM.from_pretrained(model_id, device_map='auto', quantization_config=quantization_config); print('Model loaded successfully with 4-bit quantization')"

echo Setup complete! If all steps were successful, your GPU should now be properly configured for PyTorch and bitsandbytes.

REM Additional Windows-specific troubleshooting
echo.
echo Windows-specific troubleshooting tips:
echo 1. Make sure you have the Visual C++ Redistributable installed
echo 2. Ensure your NVIDIA drivers are up to date
echo 3. If bitsandbytes-windows doesn't work, you may need to compile it from source:
echo    git clone https://github.com/Keith-Hon/bitsandbytes-windows.git
echo    cd bitsandbytes-windows
echo    pip install -e .
echo.
echo For more information, visit: https://github.com/TimDettmers/bitsandbytes/issues/156