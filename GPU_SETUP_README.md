# GPU Setup for Language Models

This directory contains several files to help you set up your GPU environment for running quantized language models. These files will help you install and configure PyTorch with CUDA support and bitsandbytes for GPU acceleration.

## Files Overview

1. **GPU_SETUP_GUIDE.md** - Comprehensive guide with detailed instructions for setting up PyTorch with CUDA support and bitsandbytes.

2. **gpu_setup_commands.sh** - Shell script with commands for Linux/macOS users to set up their GPU environment.

3. **gpu_setup_commands_windows.bat** - Batch script with commands for Windows users to set up their GPU environment.

4. **test_gpu_setup.py** - Python script to test if your GPU setup is working correctly.

## Quick Start

### Windows Users

1. Run the Windows setup script:
   ```
   gpu_setup_commands_windows.bat
   ```

2. Test your GPU setup:
   ```
   python test_gpu_setup.py
   ```

### Linux/macOS Users

1. Make the setup script executable:
   ```
   chmod +x gpu_setup_commands.sh
   ```

2. Run the setup script:
   ```
   ./gpu_setup_commands.sh
   ```

3. Test your GPU setup:
   ```
   python test_gpu_setup.py
   ```

## Troubleshooting

If you encounter issues, refer to the detailed troubleshooting section in `GPU_SETUP_GUIDE.md`.

Common issues include:

1. **CUDA not available** - Check your NVIDIA drivers and CUDA installation
2. **bitsandbytes installation fails** - Try alternative installation methods as described in the guide
3. **Model loading fails** - Check GPU memory and try different quantization settings

## Using with Our Project

After setting up your environment, you can run our local_model_chatbot_metrics.py script with:

```bash
python backend/local_model_chatbot_metrics.py --message "Your message here"
```

The script will automatically detect your GPU and use the appropriate loading strategy for the model.

## Additional Resources

- [PyTorch Installation Guide](https://pytorch.org/get-started/locally/)
- [bitsandbytes GitHub Repository](https://github.com/TimDettmers/bitsandbytes)
- [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers/index)
- [NVIDIA CUDA Installation Guide](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/index.html)