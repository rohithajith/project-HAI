from flask import Flask, render_template, request, jsonify
import os
import logging
import requests
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("admin_app")

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

@app.route('/')
def index():
    """Serve the admin dashboard page"""
    return render_template('admin.html', backend_url=BACKEND_URL)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check if backend server is running
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            return jsonify({
                "status": "ok",
                "admin_app": "running",
                "backend_server": "running"
            })
        else:
            return jsonify({
                "status": "warning",
                "admin_app": "running",
                "backend_server": "not responding properly"
            })
    except requests.RequestException:
        return jsonify({
            "status": "warning",
            "admin_app": "running",
            "backend_server": "not reachable"
        })

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 5002))
    app.run(host='0.0.0.0', port=port, debug=True)