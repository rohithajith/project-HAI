import logging
import threading
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Global variables
_model = None
_tokenizer = None
_device = None
_model_loaded = False
_model_loading = False
_model_lock = threading.Lock()

def load_model_and_tokenizer():
    """
    Load the model and tokenizer for LLM fallback, caching them.
    Uses a global flag and lock to prevent multiple simultaneous loading attempts.
    """
    global _model, _tokenizer, _device, _model_loaded, _model_loading
    
    # Fast path: check if model is already loaded without acquiring the lock
    if _model_loaded and _model is not None and _tokenizer is not None and _device is not None:
        logger.info("Using already loaded model and tokenizer")
        return _model, _tokenizer, _device
    
    # Acquire lock for thread safety
    with _model_lock:
        # Check again after acquiring the lock (double-checked locking pattern)
        if _model_loaded and _model is not None and _tokenizer is not None and _device is not None:
            logger.info("Using already loaded model and tokenizer (after lock)")
            return _model, _tokenizer, _device
        
        # If another thread/process is already loading the model, wait
        if _model_loading:
            logger.info("Model is currently being loaded by another process, waiting...")
            # Simple polling to wait for model to be loaded
            import time
            max_wait = 60  # Maximum wait time in seconds
            wait_time = 0
            while _model_loading and wait_time < max_wait:
                time.sleep(1)
                wait_time += 1
            
            if _model_loaded:
                logger.info("Model finished loading while waiting")
                return _model, _tokenizer, _device
            else:
                logger.warning(f"Timed out waiting for model to load after {max_wait}s")
        
        # Set flag to indicate model is being loaded
        _model_loading = True
    
    logger.info("Loading LLM model and tokenizer for fallback...")
    try:
        model_path = "finetunedmodel-merged"
        logger.info(f"Loading model from: {model_path}")

        _tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        _model = AutoModelForCausalLM.from_pretrained(
            model_path,
            trust_remote_code=True,
            load_in_8bit=True,  # Enable bitsandbytes quantization if needed
            device_map="auto"  # Automatically selects CUDA if available
        )

        logger.info("✅ Model loaded successfully!")
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        _model_loaded = True
        _model_loading = False
        return _model, _tokenizer, _device
    except Exception as e:
        logger.error(f"Failed to load model and tokenizer: {e}")
        _model = None
        _tokenizer = None
        _device = None
        _model_loaded = False
        _model_loading = False
        return None, None, None