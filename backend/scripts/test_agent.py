#!/usr/bin/env python
"""
Test script for Guest Request Agent
"""

import sys
import json
from pathlib import Path
import os

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Temporary direct import for testing
from backend.ai_agents.guest_request_agent import GuestRequestAgent

def run_tests():
    """Run test cases for the GuestRequestAgent"""
    agent = GuestRequestAgent()
    test_cases = [
        ("Can I get fresh towels?", "towel_request"),
        ("I need my room cleaned", "cleaning_request"),
        ("Can you wake me up at 7am?", "wakeup_call"),
        ("What time is breakfast served?", None),
        ("The TV isn't working", None)
    ]
    
    print("Running GuestRequestAgent tests...")
    print("=" * 50)
    
    for message, expected_service in test_cases:
        print(f"\nTest message: '{message}'")
        result = agent.process_request(message)
        
        print("Response:", result['response'])
        print("Service Request:", result.get('serviceRequest', False))
        if result.get('serviceRequest'):
            print("Service Type:", result['serviceType'])
            print("Frontend Update:", json.dumps(result.get('frontend_update', {}), indent=2))
        
        if expected_service:
            assert result.get('serviceType') == expected_service, \
                f"Expected {expected_service} but got {result.get('serviceType')}"
        else:
            assert not result.get('serviceRequest'), \
                f"Expected no service request but got {result.get('serviceType')}"
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    run_tests()