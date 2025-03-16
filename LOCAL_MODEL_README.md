# Local Model Chatbot for Hotel Management System

This document provides detailed information about the local model chatbot feature that has been added to the hotel management system.

## Overview

The local model chatbot allows the hotel management system to use a locally downloaded GPT-2 model for generating responses, eliminating the need for an external API. This provides several benefits:

- **Offline Operation**: The chatbot works without internet access
- **No API Key Required**: No need to obtain or manage API keys
- **No Usage Limits**: No quotas or rate limits to worry about
- **Privacy**: All data stays on your machine

## System Requirements

To run the local model effectively, your system should meet these minimum requirements:

- **CPU**: Modern multi-core processor (Intel i5/i7 or AMD Ryzen 5/7 or equivalent)
- **RAM**: 8GB minimum, 16GB recommended
- **Disk Space**: At least 1GB free space for the model and dependencies
- **GPU (Optional)**: NVIDIA GPU with CUDA support will significantly improve performance

## Installation

### 1. Install Required Python Packages

The local model requires PyTorch and Transformers libraries:

```bash
python -m pip install torch transformers
```

This will download:
- PyTorch (machine learning framework)
- Transformers (NLP library from Hugging Face)
- The GPT-2 model files (approximately 500MB)

### 2. Verify Installation

Run the test script to verify that everything is installed correctly and to check GPU availability:

```bash
python test_gpu_and_model.py
```

This script will:
- Check if PyTorch and Transformers are installed
- Detect if a GPU is available and display its information
- Test loading the GPT-2 model
- Generate a sample response

### 3. Configure the Backend

The local model is enabled by default. If you want to switch to the API mode:

1. Open `backend/controllers/chatbotController.js`
2. Change `USE_LOCAL_MODEL` to `false`:
   ```javascript
   const USE_LOCAL_MODEL = false; // Set to false to use the Hugging Face API
   ```

## How It Works

The local model chatbot works as follows:

1. The frontend sends a message to the backend API
2. The backend executes the `local_model_chatbot.py` script
3. The script loads the GPT-2 model (if not already loaded)
4. The model generates a response based on the conversation history
5. The response is sent back to the frontend

## Performance Considerations

- **First Run**: The first time you use the chatbot, it may take a few seconds to load the model
- **Subsequent Runs**: After the initial load, responses should be generated more quickly
- **GPU Acceleration**: If you have a compatible NVIDIA GPU, the model will use it automatically
- **Memory Usage**: The model uses approximately 500MB of RAM when loaded

## Customization

You can customize the local model behavior by modifying these files:

- `backend/local_model_chatbot.py`: Change model parameters like temperature, max tokens, etc.
- `backend/controllers/chatbotController.js`: Switch between local and API modes

## Troubleshooting

### Common Issues

1. **"No module named 'torch' or 'transformers'"**
   - Solution: Install the required packages with `python -m pip install torch transformers`

2. **Slow Response Times**
   - Solution: Check if you have a compatible GPU. If not, responses will be slower as the model runs on CPU

3. **Out of Memory Errors**
   - Solution: Close other memory-intensive applications or consider using a machine with more RAM

4. **CUDA Errors**
   - Solution: Update your GPU drivers or switch to CPU mode by forcing `device = "cpu"` in the script

## Advanced Configuration

For advanced users who want to customize the model further:

### Using a Different Model

You can modify the `MODEL_NAME` variable in `backend/local_model_chatbot.py` to use a different model:

```python
# Model configuration
MODEL_NAME = "gpt2-medium"  # Larger model with better quality (1.5GB)
```

Available options include:
- `gpt2` (default, 500MB)
- `gpt2-medium` (1.5GB)
- `distilgpt2` (smaller, faster, 330MB)

Note that larger models require more RAM and processing power.

### Adjusting Generation Parameters

You can modify the generation parameters in the `generate_response` function:

```python
output = model.generate(
    inputs["input_ids"],
    max_new_tokens=100,  # Increase for longer responses
    temperature=0.7,     # Higher for more creative, lower for more focused
    top_p=0.9,           # Controls diversity
    do_sample=True,      # Use sampling instead of greedy decoding
    pad_token_id=tokenizer.eos_token_id
)