"""
Script to run the TextProcessor tests.

This script sets up the environment and runs the tests for the TextProcessor class
to verify that it works correctly with the local finetuned model.
"""

import os
import sys
import unittest
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up the Python path to include the project root."""
    # Get the project root directory (3 levels up from this script)
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent.parent.parent
    
    # Add project root to Python path if not already there
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        logger.info(f"Added {project_root} to Python path")
    
    # Log environment information
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Project root: {project_root}")

def run_tests():
    """Run the TextProcessor tests."""
    from backend.ai_agents.rag.test_processor import TestTextProcessor
    
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTextProcessor)
    
    # Run the tests
    logger.info("Running TextProcessor tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    
    # Log the results
    logger.info(f"Tests run: {result.testsRun}")
    logger.info(f"Errors: {len(result.errors)}")
    logger.info(f"Failures: {len(result.failures)}")
    
    # Print any errors or failures
    if result.errors:
        logger.error("Test errors:")
        for test, error in result.errors:
            logger.error(f"{test}: {error}")
    
    if result.failures:
        logger.error("Test failures:")
        for test, failure in result.failures:
            logger.error(f"{test}: {failure}")
    
    # Return True if all tests passed
    return len(result.errors) == 0 and len(result.failures) == 0

def check_model_availability():
    """Check if the finetuned model is available."""
    try:
        from backend.ai_agents.models import get_model_info
        
        # Get model info
        model_info = get_model_info("finetuned")
        
        # Log model information
        logger.info(f"Model information: {model_info}")
        
        return model_info.get("is_loaded", False)
    except Exception as e:
        logger.error(f"Error checking model availability: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting processor test script")
    
    # Set up the environment
    setup_environment()
    
    # Check if the model is available
    logger.info("Checking model availability...")
    model_available = check_model_availability()
    
    if model_available:
        logger.info("Finetuned model is available")
    else:
        logger.warning("Finetuned model is not available. Some tests may fail.")
    
    # Run the tests
    success = run_tests()
    
    # Exit with appropriate status code
    if success:
        logger.info("All tests passed!")
        sys.exit(0)
    else:
        logger.error("Some tests failed.")
        sys.exit(1)