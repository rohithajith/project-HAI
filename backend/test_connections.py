import socketio
import time
import logging
from local_model_chatbot import load_model_and_tokenizer
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for maximum verbosity
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("test_connections")

def test_llm():
    """Test LLM loading and basic inference"""
    logger.info("Testing LLM connection...")
    try:
        model, tokenizer, device = load_model_and_tokenizer()
        logger.info("✅ LLM loaded successfully")
        
        # Test basic inference
        test_input = "Hello, how are you?"
        inputs = tokenizer(test_input, return_tensors="pt").to(device)
        outputs = model.generate(**inputs, max_length=100)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        logger.info(f"✅ LLM test response: {response}")
        return True
    except Exception as e:
        logger.error(f"❌ LLM test failed: {e}", exc_info=True)
        return False

def test_backend_connection():
    """Test connection to backend WebSocket server and LLM response"""
    logger.info("Testing backend WebSocket connection and LLM response...")
    try:
        # Create Socket.IO client
        sio = socketio.Client(logger=True, engineio_logger=True)
        connected = False
        received_responses = []
        
        @sio.on('connect')
        def on_connect():
            nonlocal connected
            logger.info("✅ Connected to backend server")
            connected = True
        
        @sio.on('message')
        def on_message(data):
            nonlocal received_responses
            logger.info(f"✅ Received response from backend: {data}")
            received_responses.append(data)
            
        # Connect to backend
        sio.connect('http://localhost:5002', wait_timeout=5)
        time.sleep(2)  # Wait for connection
        
        if not connected:
            logger.error("❌ Failed to connect to backend")
            return False
            
        # Send test message that should trigger LLM
        test_message = "What services does this hotel offer?"
        logger.info(f"Sending test message to backend: {test_message}")
        sio.emit('message', {
            'message': test_message,
            'history': []
        })
        
        # Wait for response with periodic status updates
        timeout = 60  # Increased timeout to 60 seconds for LLM processing
        check_interval = 2  # Check every 2 seconds
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check for valid response in received messages
            valid_response = False
            for response in received_responses:
                if ('response' in response and
                    len(response['response']) > 0 and
                    response['response'] != 'Connected to server' and
                    'hotel' in response['response'].lower()):  # Check for relevant content
                    logger.info("✅ Received valid LLM response")
                    logger.info(f"LLM Response: {response['response']}")
                    valid_response = True
                    break
            
            if valid_response:
                break
                
            # Log waiting status periodically
            elapsed = time.time() - start_time
            logger.info(f"Waiting for LLM response... ({elapsed:.1f}s elapsed)")
            time.sleep(check_interval)
        
        if not valid_response:
            logger.error("❌ No valid LLM response received after timeout")
            logger.error(f"Received responses: {received_responses}")
            return False
            
        sio.disconnect()
        return True
    except Exception as e:
        logger.error(f"❌ Backend connection test failed: {e}", exc_info=True)
        return False

def test_frontend_connection():
    """Test connection from frontend perspective and message forwarding"""
    logger.info("Testing frontend WebSocket connection and message forwarding...")
    try:
        # Create Socket.IO client simulating frontend
        sio = socketio.Client(logger=True, engineio_logger=True)
        connected = False
        received_responses = []
        
        @sio.on('connect')
        def on_connect():
            nonlocal connected
            logger.info("✅ Connected from frontend perspective")
            connected = True
            
        @sio.on('message')
        def on_message(data):
            nonlocal received_responses
            logger.info(f"✅ Frontend received message: {data}")
            received_responses.append(data)
            
        # Connect to frontend server
        sio.connect('http://localhost:5001', wait_timeout=5)
        time.sleep(2)  # Wait for connection
        
        if not connected:
            logger.error("❌ Failed to connect from frontend")
            return False
            
        # Send test message through frontend
        test_message = "What restaurants are nearby?"
        logger.info(f"Sending test message through frontend: {test_message}")
        sio.emit('message', {
            'message': test_message,
            'history': []
        })
        
        # Wait for response with periodic status updates
        timeout = 60  # Increased timeout to 60 seconds for full message flow
        check_interval = 2  # Check every 2 seconds
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check for valid response in received messages
            valid_response = False
            for response in received_responses:
                if ('response' in response and
                    len(response['response']) > 0 and
                    response['response'] != 'Connected to server' and
                    'restaurant' in response['response'].lower()):  # Check for relevant content
                    logger.info("✅ Received valid forwarded response")
                    logger.info(f"Forwarded Response: {response['response']}")
                    valid_response = True
                    break
            
            if valid_response:
                break
                
            # Log waiting status periodically
            elapsed = time.time() - start_time
            logger.info(f"Waiting for forwarded response... ({elapsed:.1f}s elapsed)")
            time.sleep(check_interval)
        
        if not valid_response:
            logger.error("❌ No valid forwarded response received after timeout")
            logger.error(f"Received responses: {received_responses}")
            return False
            
        sio.disconnect()
        return True
    except Exception as e:
        logger.error(f"❌ Frontend connection test failed: {e}", exc_info=True)
        return False

def run_all_tests():
    """Run all connectivity tests"""
    logger.info("Starting connectivity tests...")
    
    # Test LLM
    llm_success = test_llm()
    logger.info(f"LLM Test: {'✅ PASSED' if llm_success else '❌ FAILED'}")
    
    # Test backend connection
    backend_success = test_backend_connection()
    logger.info(f"Backend Connection Test: {'✅ PASSED' if backend_success else '❌ FAILED'}")
    
    # Test frontend connection
    frontend_success = test_frontend_connection()
    logger.info(f"Frontend Connection Test: {'✅ PASSED' if frontend_success else '❌ FAILED'}")
    
    # Overall status
    all_passed = all([llm_success, backend_success, frontend_success])
    logger.info(f"\nOverall Test Status: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)