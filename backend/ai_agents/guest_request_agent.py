#!/usr/bin/env python
"""
Guest Request Agent for Hotel Management System
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any

from backend.ai_agents.model_utils import (
    load_model_and_tokenizer,
    format_prompt,
    generate_response
)
from backend.ai_agents.utils import notify_admin_dashboard

class GuestRequestAgent:
    def __init__(self):
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("guest_request_agent")

        self.service_keywords = {
            'towel': 'towel_request',
            'towels': 'towel_request',
            'clean': 'cleaning_request',
            'room service': 'room_service',
            'wake-up': 'wakeup_call',
            'wake up': 'wakeup_call' # Added keyword without hyphen
        }

        # Use relative path from project root (where scripts are usually run)
        model_path = "finetunedmodel-merged" # Corrected path - model is in project root
        # Cache dir can still be absolute or relative, let's keep it relative for consistency
        cache_dir = "backend/models" # Cache can stay within backend

        self.model, self.tokenizer, self.device = load_model_and_tokenizer(
            model_path,
            cache_dir
        )

    def process_request(self, message: str, history: list = None) -> Dict[str, Any]:
        """Process guest request and return response"""
        try:
            # Generate initial response
            prompt = format_prompt(message, json.dumps(history) if history else None)
            response = generate_response(self.model, self.tokenizer, prompt, self.device)

            # Check for service keywords
            lower_message = message.lower() # Store lowercase message
            self.logger.info(f"Checking message: '{lower_message}'") # Log message
            service_type = None
            for keyword, service in self.service_keywords.items():
                match = keyword in lower_message
                self.logger.info(f"  - Checking keyword '{keyword}': {match}") # Log each check
                if match:
                    service_type = service
                    break # Found a match, stop checking

            # Prepare output
            output = {
                'response': response,
                'serviceRequest': service_type is not None,
                'serviceType': service_type
            }
            
            # Handle service requests
            if service_type:
                if notify_admin_dashboard(message):
                    output['response'] = f"I've noted your {service_type.replace('_', ' ')}. Our staff will assist you shortly."
                else:
                    output['response'] = "I couldn't process your request. Please contact the front desk."
                
                output['frontend_update'] = {
                    'type': 'notification',
                    'data': {
                        'message': f"Guest request: {message}",
                        'service_type': service_type,
                        'status': 'pending'
                    }
                }
            
            return output
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {
                'response': "I encountered an error processing your request. Please try again.",
                'serviceRequest': False
            }

if __name__ == "__main__":
    agent = GuestRequestAgent()
    test_message = "Can I get fresh towels for room 42?"
    print(agent.process_request(test_message))