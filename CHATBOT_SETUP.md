# AI Chatbot Integration & Configuration Guide

## 1. Introduction

This document details the setup, configuration, and operational principles of the integrated AI chatbot assistant within the Project HAI framework. The chatbot leverages Large Language Models (LLMs) to provide intelligent, context-aware assistance for hotel guests and potentially staff, enhancing user interaction and automating query resolution.

## 2. System Capabilities

The AI chatbot integration provides the following core capabilities:

*   **Ubiquitous Access**: A floating chat interface is available across the application frontend.
*   **Conversational AI**: Enables real-time interaction with an LLM-powered assistant.
*   **Contextual Awareness**: Utilizes a configurable system prompt to align responses with hotel-specific information and persona.
*   **Flexible Deployment**: Supports both locally hosted LLMs (default) and external API-based models.
*   **Efficient Backend Integration**: Employs Python bridge scripts for optimized communication between the Node.js backend and the LLM inference engine.

## 3. Initial Setup Procedure

### 3.1. Model Deployment Strategy Selection

Project HAI offers two primary modes for chatbot operation:

1.  **Local Model Deployment (Default)**: Utilizes a locally stored LLM (e.g., `finetunedmodel-merged`, based on GPT-2 architecture) for complete offline operation and data privacy. This is the recommended mode for environments prioritizing self-sufficiency.
2.  **API-Based Deployment**: Leverages external LLM APIs (e.g., Hugging Face Inference API). This requires an active internet connection and API credentials but reduces local resource requirements.

The system defaults to the Local Model Deployment.

### 3.2. Dependency Installation

#### 3.2.1. Python Environment (Required for Local Model)

Ensure Python (v3.8+) and pip are installed. Navigate to the `backend` directory and install necessary libraries:

```bash
# Navigate to backend directory
cd backend

# Create and activate a virtual environment (recommended)
python -m venv venv
# On Linux/macOS: source venv/bin/activate
# On Windows: .\venv\Scripts\activate

# Install required Python packages from root requirements file
pip install -r ../requirements.txt
```

This process installs libraries such as `torch`, `transformers`, and potentially `bitsandbytes` (for GPU optimization), and may trigger the download of the default local model if not already present.

#### 3.2.2. Node.js Environment

Install Node.js dependencies for both backend and frontend components from the project root:

```bash
# From project root directory
npm run install:all
```
Or individually:
```bash
# Install backend dependencies
cd backend
npm install

# Install frontend dependencies
cd ../frontend
npm install
```

### 3.3. Backend Configuration (API Mode Only)

To utilize the API-Based Deployment:

1.  Modify the `USE_LOCAL_MODEL` flag in `backend/controllers/chatbotController.js`:
    ```javascript
    // Set to false to enable API-based model interaction
    const USE_LOCAL_MODEL = false;
    ```

2.  Obtain API credentials from the chosen provider (e.g., Hugging Face Access Token).

3.  Add the credentials to the backend environment configuration file (`backend/.env`):
    ```dotenv
    # Example for Hugging Face API
    HF_API_KEY=your_hugging_face_api_token
    ```

### 3.4. Application Launch

Start the integrated system from the project root directory:

```bash
# From project root
npm start
```
Alternatively, run backend and frontend separately for development (see main `README.md`).

## 4. User Interaction

1.  Access the application frontend via `http://localhost:3000`.
2.  Engage the chatbot using the floating action button (typically bottom-right).
3.  Submit queries or requests through the chat interface. The system will route the message through the backend to the configured LLM (local or API) for processing.

## 5. System Customization

### 5.1. Prompt Engineering

The AI's persona, knowledge scope, and response style can be tailored by modifying the `SYSTEM_PROMPT` variable within the relevant backend controller (`backend/controllers/chatbotController.js`) or Python script (`backend/local_model_chatbot.py`, `backend/chatbot_bridge.py`).

```javascript
// Example System Prompt in chatbotController.js
const SYSTEM_PROMPT = 'You are a professional and efficient AI concierge for the Grand Hotel. Assist guests with booking inquiries, service requests, and general hotel information.';
```

### 5.2. User Interface Styling

The visual appearance of the chat interface can be adjusted by modifying the React components located in `frontend/src/components/chatbot/`, primarily `ChatbotButton.js` and `ChatbotInterface.js`, leveraging Material-UI's theming and styling capabilities.

## 6. Troubleshooting Common Issues

### 6.1. Local Model Execution Errors

*   **Dependency Errors (`ModuleNotFoundError`)**: Ensure all Python packages in `requirements.txt` are installed within the correct virtual environment (`pip install -r ../requirements.txt`).
*   **Model Loading Failures**: Verify sufficient disk space (~1GB+) and RAM (8GB+, 16GB recommended). Check model file integrity if manually downloaded. Consult `LOCAL_MODEL_README.md` for GPU/CUDA specific issues.
*   **Performance Bottlenecks**: Local model inference is CPU-intensive. Performance significantly improves with a compatible NVIDIA GPU and correctly installed CUDA drivers/toolkits.

### 6.2. API Mode Connectivity Errors

*   **Authentication Failures**: Confirm the API key (`HF_API_KEY` in `.env`) is correct and has the required permissions.
*   **Network Issues**: Ensure the backend server has internet connectivity. Check for firewall restrictions.
*   **Rate Limiting/Quotas**: Verify usage against the API provider's limits.

### 6.3. Suboptimal Response Quality

*   **Refine System Prompt**: Adjust the `SYSTEM_PROMPT` for clarity and specificity regarding the desired AI behavior.
*   **Adjust Generation Parameters**: Modify parameters like `temperature`, `max_new_tokens`, `top_p` in `backend/local_model_chatbot.py` (for local model) or potentially in the API call configuration. See `LOCAL_MODEL_README.md` for details.
*   **Consider Model Choice**: If using the local model, experiment with different model sizes (`gpt2`, `gpt2-medium`, `distilgpt2`) as detailed in `LOCAL_MODEL_README.md`.

## 7. Technical Architecture Summary

*   **Frontend**: React components manage the chat UI state and communicate user messages to the backend API endpoint (`/api/chatbot`).
*   **Backend (Node.js)**:
    *   Receives chat messages via the Express API route.
    *   Determines whether to use the local model or an external API based on the `USE_LOCAL_MODEL` flag.
    *   Invokes the appropriate Python bridge script (`local_model_chatbot.py` or `chatbot_bridge.py`) using `child_process`, passing the message and history.
    *   Relays the response from the Python script back to the frontend.
*   **Backend (Python)**:
    *   **`local_model_chatbot.py`**: Loads the specified local transformer model (e.g., GPT-2) using the `transformers` library, formats the input prompt (including history and system prompt), performs inference (preferably on GPU if available), and returns the generated text.
    *   **`chatbot_bridge.py`**: Formats the prompt and forwards the request to the configured external LLM API, handling authentication and response parsing.

This decoupled architecture allows leveraging Python's extensive AI/ML ecosystem while maintaining a robust Node.js web server, offering flexibility in LLM deployment strategies.