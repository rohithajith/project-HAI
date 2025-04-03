import os
import json
from datetime import datetime, timezone
import uuid

class AgentLogger:
    """Centralized logging mechanism for agent interactions."""
    
    @staticmethod
    def log_agent_interaction(agent_name: str, message: str, response: dict):
        """
        Log agent interactions with detailed information.
        
        Args:
            agent_name: Name of the agent handling the interaction
            message: User's original message
            response: Agent's response dictionary
        """
        # Ensure logs directory exists
        logs_dir = os.path.join(os.getcwd(), 'agent_logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Generate unique log filename
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        log_filename = os.path.join(logs_dir, f"{agent_name}_interaction_{timestamp}_{uuid.uuid4().hex[:8]}.json")
        
        # Prepare log entry
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent_name,
            "message": message,
            "response": response,
            "frontend_update": response.get('frontend_update', {})
        }
        
        # Write log file
        with open(log_filename, 'w') as log_file:
            json.dump(log_entry, log_file, indent=2)
        
        return log_filename

    @staticmethod
    def get_recent_logs(agent_name=None, limit=10):
        """
        Retrieve recent log files.
        
        Args:
            agent_name: Optional filter for agent name
            limit: Maximum number of log files to return
        
        Returns:
            List of recent log file paths
        """
        logs_dir = os.path.join(os.getcwd(), 'agent_logs')
        
        # Get all log files
        log_files = [
            os.path.join(logs_dir, f) 
            for f in os.listdir(logs_dir) 
            if f.endswith('.json') and (agent_name is None or agent_name in f)
        ]
        
        # Sort by modification time, most recent first
        log_files.sort(key=os.path.getmtime, reverse=True)
        
        return log_files[:limit]