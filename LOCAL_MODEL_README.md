# Project HAI: Local LLM Deployment Guide

## 1. Overview

This document provides technical specifications and operational guidance for deploying the AI chatbot component of Project HAI using a locally hosted Large Language Model (LLM). This deployment strategy prioritizes offline capability, data privacy, and operational autonomy by eliminating reliance on external APIs for core chatbot functionality.

The default local model is `finetunedmodel-merged`, derived from the GPT-2 architecture, offering a balance between performance and resource requirements.

## 2. Advantages of Local Deployment

Utilizing a local LLM offers significant advantages:

*   **Offline Functionality**: Enables continuous chatbot operation without requiring an active internet connection post-setup.
*   **Data Privacy & Security**: Ensures all conversational data remains within the local environment, critical for handling sensitive guest information.
*   **No External Dependencies**: Eliminates reliance on third-party API providers, avoiding potential costs, rate limits, or service disruptions.
*   **Predictable Performance**: Consistent response times after initial model loading, independent of external network latency.
*   **Customization Potential**: Allows for fine-tuning or replacement with custom-trained models tailored to specific hotel needs.

## 3. System Requirements

Effective local LLM inference necessitates adequate hardware resources:

*   **Processor (CPU)**: A modern multi-core processor (e.g., Intel Core i5/i7 8th Gen+, AMD Ryzen 5/7 3000 series+) is recommended for acceptable performance if no GPU is available.
*   **Memory (RAM)**:
    *   Minimum: 8 GB
    *   Recommended: 16 GB or more (especially if running larger models or other demanding applications concurrently).
*   **Storage**: Minimum 1-2 GB free disk space for Python dependencies and the default model (`finetunedmodel-merged` or `gpt2`). Larger models require significantly more space.
*   **Graphics Processor (GPU) (Highly Recommended)**:
    *   An NVIDIA GPU with CUDA support (Compute Capability 6.0+) dramatically accelerates inference speed.
    *   Requires appropriate NVIDIA drivers and potentially the CUDA Toolkit installed.
    *   Libraries like `bitsandbytes` (installed via `requirements.txt`) enable optimized inference (e.g., 4-bit/8-bit quantization) on compatible GPUs, reducing VRAM usage.

## 4. Installation and Verification

### 4.1. Python Environment Setup

Refer to Section 3.2.1 in `CHATBOT_SETUP.md` for instructions on setting up the Python virtual environment and installing dependencies using `pip install -r ../requirements.txt`. This step installs `torch`, `transformers`, and other necessary packages.

### 4.2. Installation Verification Script

Execute the provided test script from the `backend` directory to confirm the environment and model loading capabilities:

```bash
# Ensure your Python virtual environment is activated
python test_gpu_and_model.py
```

This script performs crucial checks:
*   Confirms the presence of `torch` and `transformers`.
*   Detects CUDA availability and compatible NVIDIA GPUs.
*   Attempts to load the default local model (`finetunedmodel-merged`).
*   Executes a sample inference task to verify functionality.

Review the script's output for any errors or warnings regarding GPU detection or model loading.

### 4.3. Backend Configuration

The local model is the default operational mode. No specific configuration is required unless switching *away* from local mode to API mode, as described in `CHATBOT_SETUP.md`. The relevant flag is in `backend/controllers/chatbotController.js`:

```javascript
// Default setting for local model usage
const USE_LOCAL_MODEL = true;
```

## 5. Operational Workflow

The local chatbot interaction follows this sequence:

1.  **Frontend Request**: User input is captured by the React frontend and sent to the `/api/chatbot` backend endpoint.
2.  **Backend Routing**: The Node.js controller identifies `USE_LOCAL_MODEL` is `true` and prepares to invoke the local processing script.
3.  **Python Script Execution**: The backend executes `backend/local_model_chatbot.py` via `child_process`, passing the user message and conversation history.
4.  **Model Loading & Inference**:
    *   The Python script initializes the `transformers` pipeline.
    *   It loads the specified `MODEL_NAME` (e.g., `finetunedmodel-merged`) and tokenizer into memory (CPU or GPU). This occurs only once per script execution or backend process lifetime, depending on implementation details.
    *   The input prompt is constructed using the system prompt, conversation history, and the new user message.
    *   The LLM generates a response based on the input prompt.
5.  **Response Transmission**: The generated text is captured from the Python script's standard output by the Node.js backend.
6.  **Frontend Update**: The backend sends the response back to the frontend, which updates the chat interface.

## 6. Performance Characteristics

*   **Initialization Latency**: The first chatbot request after starting the backend may experience a delay (seconds to tens of seconds) while the model is loaded into RAM/VRAM.
*   **Inference Time**: Subsequent requests are typically faster.
    *   **CPU**: Response times can range from a few seconds to over a minute, depending on CPU power and response length.
    *   **GPU**: Response times are significantly reduced, often to a few seconds, depending on GPU capability.
*   **Resource Consumption**:
    *   **RAM**: The default model consumes ~500MB+ of RAM. Larger models require proportionally more.
    *   **VRAM (GPU)**: Usage depends on the model size and quantization level (e.g., 4-bit quantization significantly reduces VRAM needs compared to FP16).

## 7. Customization and Advanced Configuration

### 7.1. Model Selection

Modify the `MODEL_NAME` variable in `backend/local_model_chatbot.py` to experiment with different pre-trained models available via the Hugging Face Hub (ensure they are compatible with `AutoModelForCausalLM`):

```python
# In backend/local_model_chatbot.py
# Default: Uses the fine-tuned model path
MODEL_NAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "finetunedmodel-merged")

# Alternative Example: Standard GPT-2 Medium
# MODEL_NAME = "gpt2-medium" # Requires ~1.5GB disk space + more RAM/VRAM

# Alternative Example: DistilGPT-2 (smaller, faster)
# MODEL_NAME = "distilgpt2" # Requires ~330MB disk space
```
*Note: Changing the model requires re-running the setup or ensuring the new model is downloaded.*

### 7.2. Inference Parameter Tuning

Adjust text generation parameters within the `generate_response` function in `backend/local_model_chatbot.py` to influence response characteristics:

```python
output = model.generate(
    inputs["input_ids"],
    max_new_tokens=100,  # Max length of the generated response
    temperature=0.7,     # Controls randomness (0.1=focused, 1.0=creative)
    top_p=0.9,           # Nucleus sampling probability threshold
    do_sample=True,      # Enables sampling-based generation
    pad_token_id=tokenizer.eos_token_id
)
```

### 7.3. Quantization and Optimization (GPU)

The `local_model_chatbot_metrics.py` (and potentially `local_model_chatbot.py`) script attempts to use `bitsandbytes` for 4-bit quantization on compatible NVIDIA GPUs. This significantly reduces memory usage and can improve speed. Ensure `bitsandbytes` is installed (`pip install bitsandbytes`) and your CUDA environment is correctly configured. If issues arise, the script may fall back to FP16 or CPU execution.

## 8. Troubleshooting Guide

### 8.1. Installation & Dependency Issues

*   **`ModuleNotFoundError: No module named 'torch'` / `'transformers'` / `'bitsandbytes'`**: Re-run `pip install -r ../requirements.txt` within the activated virtual environment. Verify pip is installing to the correct environment.
*   **`bitsandbytes` Errors**: Often related to incompatible CUDA versions or missing prerequisites. Consult the `bitsandbytes` documentation for specific CUDA/driver requirements. Consider reinstalling it.

### 8.2. Performance Problems

*   **Slow Responses**: Primarily occurs on CPU-only systems. Ensure no unnecessary background processes are consuming CPU/RAM. Consider upgrading hardware or using a smaller model (`distilgpt2`). If a GPU is present but not used, investigate driver/CUDA installation issues using `test_gpu_and_model.py`.
*   **High Memory Usage / Crashes**: The default model requires substantial RAM. Close other applications. If using larger models (`gpt2-medium`, etc.), ensure sufficient RAM (16GB+). On GPU, ensure sufficient VRAM; 4-bit quantization helps mitigate this.

### 8.3. CUDA / GPU Errors

*   **`CUDA out of memory`**: The GPU does not have enough VRAM for the model at the current precision. Ensure `bitsandbytes` is working for quantization, try a smaller model, or reduce batch size if applicable (though less relevant for single-response generation).
*   **`Torch not compiled with CUDA enabled`**: The installed PyTorch version does not support your GPU/CUDA setup. Ensure you installed the correct PyTorch version for your CUDA toolkit version (see PyTorch official website).
*   **Driver Mismatches**: Ensure your NVIDIA driver version is compatible with the installed CUDA Toolkit version and PyTorch.

Refer to the output of `test_gpu_and_model.py` and specific error messages for detailed diagnostics.