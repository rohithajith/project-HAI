#!/usr/bin/env python
"""
Local Model Chatbot Script for Hotel Management System

This script first attempts to process messages using an AgentManager.
If no agent handles the message, it falls back to using a locally
downloaded model (GPT-2) to generate responses.

Usage:
    python local_model_chatbot.py --message "User message" [--history "JSON history string"]

Requirements:
    - torch
    - transformers
    - langgraph
    - pydantic
    - Other dependencies from requirements.txt
"""

import argparse
import json
import os
import sys
import logging
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("local_model_chatbot")

# --- Agent Integration ---
# Add path to backend directory to import ai_agents
# Assumes this script is run from the 'backend' directory or paths are adjusted accordingly
try:
    # Adjust path if necessary based on execution context
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    from ai_agents.agent_manager import AgentManagerCorrected
    from ai_agents.base_agent import AgentOutput
    # Instantiate Agent Manager (consider caching/singleton in a real app)
    agent_manager = AgentManagerCorrected()
    logger.info("Agent Manager initialized.")
except ImportError as e:
    logger.error(f"Failed to import agent modules: {e}")
    logger.error("Ensure agents are correctly placed and PYTHONPATH is set if needed.")
    agent_manager = None # Flag that agents are unavailable
except Exception as e:
    logger.error(f"Error initializing Agent Manager: {e}")
    agent_manager = None
# --- End Agent Integration ---


# System prompt for the hotel AI assistant (used for LLM fallback)
SYSTEM_PROMPT = "you are a helpfull hotel ai which acts like hotel reception udating requests and handiling queries from users"

# Model configuration (used for LLM fallback)
MODEL_NAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "finetunedmodel-merged")
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

# --- LLM Fallback Functions ---
_model = None
_tokenizer = None
_device = None

def load_model_and_tokenizer():
    """Load the model and tokenizer for LLM fallback, caching them."""
    global _model, _tokenizer, _device
    if _model is not None and _tokenizer is not None and _device is not None:
        return _model, _tokenizer, _device

    logger.info("Loading LLM model and tokenizer for fallback...")
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        import torch

        if not torch.cuda.is_available():
            logger.warning("CUDA not available for LLM fallback. Using CPU.")
            _device = "cpu"
        else:
            _device = "cuda"
            logger.info(f"Using device for LLM fallback: {_device}")

        logger.info(f"Loading tokenizer from {MODEL_NAME}")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=MODEL_DIR)

        if _device == "cuda":
            try:
                import bitsandbytes as bnb
                logger.info(f"Using bitsandbytes version: {bnb.__version__}")
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
                logger.info("Loading LLM model with 4-bit quantization")
                _model = AutoModelForCausalLM.from_pretrained(
                    MODEL_NAME, cache_dir=MODEL_DIR, device_map="auto", quantization_config=quantization_config
                )
            except (ImportError, Exception) as e:
                logger.warning(f"Failed LLM quantization: {e}. Falling back to FP16.")
                _model = AutoModelForCausalLM.from_pretrained(
                    MODEL_NAME, cache_dir=MODEL_DIR, torch_dtype=torch.float16, device_map="auto"
                )
        else:
            logger.info("Loading LLM model on CPU")
            _model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME, cache_dir=MODEL_DIR, low_cpu_mem_usage=True
            ).to(_device)

        logger.info("LLM model and tokenizer loaded.")
        return _model, _tokenizer, _device
    except ImportError as e:
        logger.error(f"Error importing modules for LLM fallback: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading LLM fallback model: {e}")
        raise

def format_prompt(message, history: List[Dict[str, Any]]):
    """Format the conversation history into a prompt for the LLM fallback"""
    prompt = f"{SYSTEM_PROMPT}\n\n"
    for msg in history:
        # Adjust role mapping if needed based on actual history format
        role = "Hotel AI" if msg.get("role") == "assistant" or msg.get("role") == "system" else "User"
        prompt += f"{role}: {msg.get('content', '')}\n"
    prompt += f"User: {message}\nHotel AI:"
    return prompt

def generate_llm_response(model, tokenizer, prompt, device):
    """Generate a response using the local LLM fallback"""
    logger.info("Generating response using LLM fallback...")
    try:
        import torch
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            output = model.generate(
                inputs["input_ids"],
                max_new_tokens=100,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        response = tokenizer.decode(output[0], skip_special_tokens=True)
        response = response[len(prompt):].strip()

        # Clean up response
        if "User:" in response: response = response.split("User:")[0].strip()
        if "Hotel AI:" in response: response = response.split("Hotel AI:")[0].strip()
        if not response or len(response) < 5: response = "I understand. How else may I assist you?" # Generic fallback

        logger.info(f"LLM fallback response generated: {response[:50]}...")
        return response
    except Exception as e:
        logger.error(f"Error generating LLM fallback response: {e}")
        return "I apologize, but I encountered an issue processing your request with the fallback model."

# --- Main Processing Logic ---
async def process_message_async(message: str, history_json: Optional[str] = None) -> Dict[str, Any]:
    """
    Process a message using agents first, then fallback to LLM.
    Returns a dictionary with 'response' and 'notifications'.
    """
    final_result = {
        "response": "An error occurred.",
        "notifications": [],
        "error": None
    }

    try:
        # 1. Parse history
        try:
            history: List[Dict[str, Any]] = json.loads(history_json) if history_json else []
        except json.JSONDecodeError:
            logger.warning("Invalid JSON history format received. Proceeding with empty history.")
            history = []

        # 2. Run Agent Manager (if available)
        agent_output: Optional[AgentOutput] = None
        if agent_manager:
            logger.info("Running agent manager...")
            try:
                agent_output = await agent_manager.process(message, history)
                # DETAILED LOG: Log the raw output from the agent manager
                logger.info(f"DEBUG: Agent manager raw output: {agent_output!r}")
            except Exception as agent_error:
                logger.error(f"Error during agent processing: {agent_error}", exc_info=True)
                # Decide if we should still fallback or return error
                # For now, we'll try to fallback
        else:
            logger.warning("Agent manager not available.")

        # 3. Check if agent handled the request
        if agent_output and (agent_output.response or agent_output.tool_used):
            logger.info("Agent handled the request.")
            final_result = {
                "response": agent_output.response or "Your request is being processed by our team.", # Default if only tool used
                "notifications": agent_output.notifications or [],
                "error": None
            }
        else:
            # 4. Agent did not handle (or failed), fallback to LLM
            logger.info("Agent did not handle or was unavailable. Falling back to LLM.")
            try:
                model, tokenizer, device = load_model_and_tokenizer()
                prompt = format_prompt(message, history) # Use parsed history list
                llm_response = generate_llm_response(model, tokenizer, prompt, device)
                final_result = {
                    "response": llm_response,
                    "notifications": [],
                    "error": None
                }
            except Exception as llm_error:
                logger.error(f"Error during LLM fallback: {llm_error}", exc_info=True)
                final_result["error"] = f"LLM fallback failed: {str(llm_error)}"
                final_result["response"] = "I apologize, I couldn't process your request using the primary or fallback method."

    except Exception as e:
        logger.exception(f"Critical error in process_message_async: {e}")
        final_result["error"] = f"Unexpected error: {str(e)}"
        final_result["response"] = "A critical error occurred while processing your message."

    # Ensure response is never None before returning
    if final_result.get("response") is None:
        final_result["response"] = final_result.get("error", "Processing complete.")

    # Remove error key if no error occurred for cleaner JSON
    if final_result.get("error") is None:
        final_result.pop("error", None)

    # DETAILED LOG: Log the final dictionary before JSON conversion
    logger.info(f"DEBUG: Final result before JSON dump: {final_result}")
    return final_result


async def main():
    """Main async function to parse arguments and process the message"""
    parser = argparse.ArgumentParser(description="Local model chatbot for hotel management system")
    parser.add_argument("--message", required=True, help="User message")
    parser.add_argument("--history", help="JSON string of conversation history")

    args = parser.parse_args()

    # Ensure event loop is running if called directly multiple times (might not be needed depending on context)
    # loop = asyncio.get_event_loop()
    # result = await loop.create_task(process_message_async(args.message, args.history))

    result = await process_message_async(args.message, args.history)

    # Print the final JSON result to stdout for the Node.js controller
    print(json.dumps(result))

if __name__ == "__main__":
    # Ensure asyncio event loop compatibility across different environments if needed
    # if sys.platform == 'win32':
    #     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())