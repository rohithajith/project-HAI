import os
import sys
import logging
import threading
import uvicorn
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("main")

def start_fastapi():
    """Start the FastAPI server"""
    logger.info("Starting FastAPI server...")
    os.chdir('backend')
    uvicorn.run("fastapi_server:app", host="0.0.0.0", port=8000, reload=False)

def start_guest_app():
    """Start the Guest App Flask server"""
    logger.info("Starting Guest App server...")
    os.chdir('frontend/guest-app')
    from frontend.guest_app.app import app
    app.run(host='0.0.0.0', port=5001, debug=False)

def start_admin_app():
    """Start the Admin App Flask server"""
    logger.info("Starting Admin App server...")
    os.chdir('frontend/admin-app')
    from frontend.admin_app.app import app
    app.run(host='0.0.0.0', port=5002, debug=False)

def start_room_service_app():
    """Start the Room Service App Flask server"""
    logger.info("Starting Room Service App server...")
    os.chdir('frontend/room-service-app')
    from frontend.room_service_app.app import app
    app.run(host='0.0.0.0', port=5003, debug=False)

def main():
    """Start all servers"""
    logger.info("Starting Hotel AI System...")
    
    # Start FastAPI in a separate thread
    fastapi_thread = threading.Thread(target=start_fastapi)
    fastapi_thread.daemon = True
    fastapi_thread.start()
    
    # Wait for FastAPI to start
    time.sleep(2)
    
    # Start Guest App in a separate thread
    guest_app_thread = threading.Thread(target=start_guest_app)
    guest_app_thread.daemon = True
    guest_app_thread.start()
    
    # Start Admin App in a separate thread
    admin_app_thread = threading.Thread(target=start_admin_app)
    admin_app_thread.daemon = True
    admin_app_thread.start()
    
    # Start Room Service App in the main thread
    start_room_service_app()

if __name__ == "__main__":
    main()