"""
Module for loading and managing AI models.

This module provides functions to load various models used by the AI agents,
including the local finetuned model.
"""

import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

def load_finetuned_model(model_name: str = "finetuned") -> Any:
    """
    Load a local finetuned model.
    
    Args:
        model_name: Name of the model to load. Default is "finetuned".
        
    Returns:
        The loaded model object
        
    Raises:
        ImportError: If the required dependencies are not installed
        FileNotFoundError: If the model files cannot be found
        Exception: For other loading errors
    """
    logger.info(f"Loading local finetuned model: {model_name}")
    
    try:
        # Try to import spaCy as a fallback for compatibility
        import spacy
        
        # Check if we're loading the default finetuned model
        if model_name == "finetuned":
            # Path to the finetuned model directory
            # Assuming the model is in finetunedmodel-merged directory at project root
            model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                     "finetunedmodel-merged")
            
            if not os.path.exists(model_path):
                logger.warning(f"Finetuned model directory not found at {model_path}")
                logger.info("Attempting to load model by name instead")
                return spacy.load(model_name)
            
            logger.info(f"Loading model from path: {model_path}")
            return spacy.load(model_path)
        else:
            # Load by model name
            return spacy.load(model_name)
            
    except ImportError as e:
        logger.error(f"Failed to import required dependencies: {e}")
        raise ImportError(f"Required dependencies not installed: {e}")
    except FileNotFoundError as e:
        logger.error(f"Model files not found: {e}")
        raise FileNotFoundError(f"Model files not found: {e}")
    except Exception as e:
        logger.error(f"Error loading model {model_name}: {e}")
        raise Exception(f"Error loading model {model_name}: {e}")

def get_model_info(model_name: str = "finetuned") -> Dict[str, Any]:
    """
    Get information about a loaded model.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Dictionary with model information
    """
    try:
        model = load_finetuned_model(model_name)
        
        # Get basic model info
        info = {
            "name": model_name,
            "type": type(model).__name__,
            "is_loaded": model is not None
        }
        
        # Add spaCy-specific info if it's a spaCy model
        if hasattr(model, "meta"):
            info.update({
                "version": model.meta.get("version", "unknown"),
                "description": model.meta.get("description", ""),
                "author": model.meta.get("author", ""),
                "pipeline": list(model.pipe_names)
            })
            
        return info
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        return {
            "name": model_name,
            "error": str(e),
            "is_loaded": False
        }