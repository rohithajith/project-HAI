# Chatbot Integration Guide

This guide explains how to set up and use the hotel AI chatbot feature that has been integrated into your application.

## Overview

The chatbot feature adds a floating chat button to your hotel management system that allows users to interact with an AI assistant. The assistant is powered by the GPT-2 model and is configured to act as a helpful hotel reception assistant.

## Features

- Floating chat button on all pages
- Real-time conversation with AI assistant
- Hotel-specific system prompt for contextual responses
- Local GPT-2 model for offline operation
- Option to use Hugging Face API as a fallback
- Python bridge script for efficient model communication

## Setup Instructions

### 1. Choose Your Model Option

The chatbot can operate in two modes:

1. **Local Model (Default)**: Uses a locally downloaded GPT-2 model for offline operation
2. **API Mode**: Uses the Hugging Face API (requires an API key)

The local model is enabled by default and doesn't require an API key.

### 2. Install Dependencies

#### Python Dependencies
The chatbot requires PyTorch and Transformers to run the local model:

```bash
# Install Python dependencies
python -m pip install torch transformers
```

This will download the required libraries and the GPT-2 model (approximately 500MB).

#### Node.js Dependencies
Install the Node.js dependencies for both the backend and frontend:

```bash
# Install backend dependencies
cd backend
npm install

# Install frontend dependencies
cd ../frontend
npm install
```

### 3. Configure the Backend (Optional for API Mode)

If you want to use the Hugging Face API instead of the local model:

1. Open `backend/controllers/chatbotController.js` and set `USE_LOCAL_MODEL` to `false`:
   ```javascript
   const USE_LOCAL_MODEL = false; // Set to false to use the Hugging Face API
   ```

2. Get a Hugging Face API key:
   - Create an account or log in at [Hugging Face](https://huggingface.co/)
   - Go to your profile settings and navigate to "Access Tokens"
   - Create a new token with "read" access
   - Copy the generated API key

3. Open the `.env` file in the `backend` directory and add your API key:
   ```
   HF_API_KEY=your_actual_api_key_here
   ```

### 4. Start the Application

Start both the backend and frontend servers:

```bash
# From the project root
npm run start
```

## Usage

1. Navigate to any page in the application
2. Click on the chat button in the bottom-right corner to open the chat interface
3. Type your question or request and press Enter or click the send button
4. The AI assistant will respond with helpful information about the hotel

## Customization

### Modifying the System Prompt

If you want to change the behavior or personality of the AI assistant, you can modify the system prompt in the `backend/controllers/chatbotController.js` file:

```javascript
// System prompt for the hotel AI assistant
const SYSTEM_PROMPT = 'you are a helpfull hotel ai which acts like hotel reception udating requests and handiling queries from users';
```

### Styling the Chat Interface

The chat interface is built with Material-UI components. You can customize its appearance by modifying the `frontend/src/components/chatbot/ChatbotButton.js` file.

## Troubleshooting

### Local Model Issues

If you encounter errors with the local model:
- Ensure PyTorch and Transformers are correctly installed: `python -m pip install torch transformers`
- Check if you have enough disk space for the model (approximately 500MB)
- For slow responses, consider using a machine with a GPU
- If you see CUDA errors, your GPU might not be compatible - the model will fall back to CPU

### API Key Issues (When Using API Mode)

If you encounter errors related to the Hugging Face API:
- Your API key is correctly set in the `.env` file
- Your API key has the necessary permissions
- You have sufficient quota for API calls

### Model Response Issues

If the model responses are not as expected:
- Try adjusting the system prompt to be more specific
- Check the parameters in the model configuration (temperature, max_new_tokens, etc.)
- For local model, try increasing the `max_new_tokens` parameter in `local_model_chatbot.py`

## Technical Details

### Frontend

The chatbot UI is implemented as a React component using Material-UI. It maintains a conversation history and communicates with the backend API.

### Backend

The backend architecture consists of:

1. **Node.js API Endpoint**: Receives messages from the frontend
2. **Python Bridge Scripts**: Two options for model interaction
   - **Local Model Script** (`backend/local_model_chatbot.py`): Uses a locally downloaded GPT-2 model
   - **API Bridge Script** (`backend/chatbot_bridge.py`): Communicates with the Hugging Face API
   - Both are executed by the Node.js backend using child_process
   - Both manage formatting the conversation with the system prompt

#### Local Model Benefits
- Works offline without internet connection
- No API key or external service required
- No usage limits or quotas
- Faster response times for subsequent queries (after initial load)
- Complete privacy (all data stays on your machine)

#### API Model Benefits
- No need to download large model files
- Less resource-intensive on your machine
- Access to more powerful models
- No local GPU required

This architecture provides several benefits:
- Separation of concerns between the web server and AI model interaction
- Leverages Python's strong ecosystem for AI/ML tasks
- Easier maintenance and updates to the AI integration
- Better error handling and debugging capabilities
- Flexibility to choose between local and API-based models