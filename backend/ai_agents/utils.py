"""
Utility functions for the AI agents system
"""

import json
import logging
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ai_agents_utils")

def notify_admin_dashboard(guest_request):
    """Send notification to admin dashboard about guest request"""
    try:
        response = requests.post(
            'http://localhost:5000/api/hotel-info/towel-request',
            json={'request': guest_request},
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error notifying admin dashboard: {e}")
        return False