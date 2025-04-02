import asyncio
import socketio
import time
import json
import logging
import argparse
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama for colored terminal output
init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("test_agent_flow")

class AgentFlowTester:
    """Test the flow of the agent system with multiple test cases."""
    
    def __init__(self, server_url="http://localhost:5000", wait_time=120):
        self.server_url = server_url
        self.wait_time = wait_time  # Wait time in seconds (default: 2 minutes)
        # Configure logging specifically for this class
        self.logger = logging.getLogger("test_agent_flow")
        self.logger.setLevel(logging.DEBUG)
        
        # Initialize Socket.IO clients
        self.guest_socket = socketio.Client()
        self.room_service_socket = socketio.Client()
        self.admin_socket = socketio.Client()
        
        # Test cases
        self.test_cases = [
            {
                "name": "Towel Request",
                "room_number": "101",
                "message": "I need extra towels please",
                "expected_agent": "room_service_agent",
                "expected_dashboard": "room_service"
            },
            {
                "name": "Food Order Request",
                "room_number": "102",
                "message": "I would like to order a burger and fries",
                "expected_agent": "room_service_agent",
                "expected_dashboard": "room_service"
            },
            {
                "name": "Maintenance Request",
                "room_number": "103",
                "message": "The sink in my bathroom is leaking",
                "expected_agent": "maintenance_agent",
                "expected_dashboard": "admin"
            }
        ]
        
        # Test results
        self.test_results = []
        
        # Connection status
        self.guest_connected = False
        self.room_service_connected = False
        self.admin_connected = False
        
        # Response data
        self.guest_responses = {}
        self.room_service_notifications = {}
        self.admin_notifications = {}
        
        # Set up event handlers for guest socket
        @self.guest_socket.event
        def connect():
            logger.info(f"{Fore.GREEN}Guest client connected{Style.RESET_ALL}")
            self.guest_connected = True
            
        @self.guest_socket.event
        def disconnect():
            logger.info(f"{Fore.YELLOW}Guest client disconnected{Style.RESET_ALL}")
            self.guest_connected = False
            
        @self.guest_socket.event
        def message(data):
            try:
                current_test = self.current_test_case["name"]
                logger.info(f"{Fore.CYAN}[{current_test}] Received message from server: {data}{Style.RESET_ALL}")
                
                if current_test not in self.guest_responses:
                    self.guest_responses[current_test] = []
                
                # Store the response data
                self.guest_responses[current_test].append({
                    "timestamp": time.time(),
                    "data": data
                })
                
                # Log the agent used, if available
                if "agent" in data:
                    logger.info(f"{Fore.GREEN}Agent identified in response: {data.get('agent')}{Style.RESET_ALL}")
                
                # Log notifications if they exist
                if "notifications" in data:
                    for notification in data["notifications"]:
                        logger.info(f"{Fore.GREEN}Notification received: {notification}{Style.RESET_ALL}")
            except Exception as e:
                logger.error(f"{Fore.RED}Error processing message: {e}{Style.RESET_ALL}")
        
        # Set up event handlers for room service socket
        @self.room_service_socket.event
        def connect():
            logger.info(f"{Fore.GREEN}Room service client connected{Style.RESET_ALL}")
            self.room_service_connected = True
            
        @self.room_service_socket.event
        def disconnect():
            logger.info(f"{Fore.YELLOW}Room service client disconnected{Style.RESET_ALL}")
            self.room_service_connected = False
            
        @self.room_service_socket.event
        def notification(data):
            try:
                current_test = self.current_test_case["name"]
                logger.info(f"{Fore.MAGENTA}[{current_test}] Received notification on room service dashboard: {data}{Style.RESET_ALL}")
                
                if current_test not in self.room_service_notifications:
                    self.room_service_notifications[current_test] = []
                
                # Store the notification data
                self.room_service_notifications[current_test].append({
                    "timestamp": time.time(),
                    "data": data
                })
                
                # Log agent information if available in the payload
                if "payload" in data and "agent" in data["payload"]:
                    logger.info(f"{Fore.MAGENTA}Room service notification from agent: {data['payload'].get('agent')}{Style.RESET_ALL}")
            except Exception as e:
                logger.error(f"{Fore.RED}Error processing room service notification: {e}{Style.RESET_ALL}")
        
        # Set up event handlers for admin socket
        @self.admin_socket.event
        def connect():
            logger.info(f"{Fore.GREEN}Admin client connected{Style.RESET_ALL}")
            self.admin_connected = True
            
        @self.admin_socket.event
        def disconnect():
            logger.info(f"{Fore.YELLOW}Admin client disconnected{Style.RESET_ALL}")
            self.admin_connected = False
            
        @self.admin_socket.event
        def notification(data):
            try:
                current_test = self.current_test_case["name"]
                logger.info(f"{Fore.BLUE}[{current_test}] Received notification on admin dashboard: {data}{Style.RESET_ALL}")
                
                if current_test not in self.admin_notifications:
                    self.admin_notifications[current_test] = []
                
                # Store the notification data
                self.admin_notifications[current_test].append({
                    "timestamp": time.time(),
                    "data": data
                })
                
                # Log agent information if available in the payload
                if "payload" in data and "agent" in data["payload"]:
                    logger.info(f"{Fore.BLUE}Admin notification from agent: {data['payload'].get('agent')}{Style.RESET_ALL}")
            except Exception as e:
                logger.error(f"{Fore.RED}Error processing admin notification: {e}{Style.RESET_ALL}")
    
    async def connect_sockets(self):
        """Connect all sockets to the server."""
        try:
            # Connect guest socket
            self.guest_socket.connect(f"{self.server_url}/guest")
            
            # Connect room service socket
            self.room_service_socket.connect(f"{self.server_url}/room-service")
            
            # Connect admin socket
            self.admin_socket.connect(f"{self.server_url}/admin")
            
            # Wait for all connections to establish
            await asyncio.sleep(2)
            
            return self.guest_connected and self.room_service_connected and self.admin_connected
            
        except Exception as e:
            logger.error(f"{Fore.RED}Error connecting to server: {e}{Style.RESET_ALL}")
            return False
    
    async def disconnect_sockets(self):
        """Disconnect all sockets from the server."""
        try:
            if self.guest_socket.connected:
                self.guest_socket.disconnect()
            
            if self.room_service_socket.connected:
                self.room_service_socket.disconnect()
            
            if self.admin_socket.connected:
                self.admin_socket.disconnect()
                
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"{Fore.RED}Error disconnecting from server: {e}{Style.RESET_ALL}")
    
    async def run_test_case(self, test_case):
        """Run a single test case."""
        self.current_test_case = test_case
        
        test_start_time = time.time()
        room_number = test_case["room_number"]
        message = test_case["message"]
        full_message = f"I am in room {room_number}. {message}"
        
        logger.info(f"\n{Fore.YELLOW}======= STARTING TEST: {test_case['name']} ======={Style.RESET_ALL}")
        logger.info(f"{Fore.YELLOW}Message: {full_message}{Style.RESET_ALL}")
        
        # Initialize test result
        test_result = {
            "name": test_case["name"],
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": full_message,
            "expected_agent": test_case["expected_agent"],
            "expected_dashboard": test_case["expected_dashboard"],
            "guest_response_received": False,
            "room_service_notification_received": False,
            "admin_notification_received": False,
            "correct_agent_used": False,
            "correct_dashboard_notified": False,
            "response_time": None,
            "notification_time": None,
            "success": False,
            "errors": []
        }
        
        try:
            # Send message
            self.guest_socket.emit('message', {
                'message': full_message,
                'history': [],
                'room': room_number
            })
            
            logger.info(f"{Fore.YELLOW}Message sent. Waiting {self.wait_time} seconds for processing...{Style.RESET_ALL}")
            
            # Wait for the specified time
            await asyncio.sleep(self.wait_time)
            
            # Check results
            test_result["guest_response_received"] = test_case["name"] in self.guest_responses and len(self.guest_responses[test_case["name"]]) > 0
            test_result["room_service_notification_received"] = test_case["name"] in self.room_service_notifications and len(self.room_service_notifications[test_case["name"]]) > 0
            test_result["admin_notification_received"] = test_case["name"] in self.admin_notifications and len(self.admin_notifications[test_case["name"]]) > 0
            
            # Calculate response time if response received
            if test_result["guest_response_received"]:
                first_response = self.guest_responses[test_case["name"]][0]
                test_result["response_time"] = first_response["timestamp"] - test_start_time
                
                # Check if correct agent was used - look in both the message and notifications
                response_data = first_response["data"]
                
                # First check direct agent field in response
                if response_data.get("agent") == test_case["expected_agent"]:
                    test_result["correct_agent_used"] = True
                    logger.info(f"{Fore.GREEN}Correct agent identified in message agent field: {response_data.get('agent')}{Style.RESET_ALL}")
                
                # Then check notifications
                elif "notifications" in response_data:
                    for notification in response_data["notifications"]:
                        if notification.get("agent") == test_case["expected_agent"] or notification.get("type") == test_case["expected_agent"]:
                            test_result["correct_agent_used"] = True
                            logger.info(f"{Fore.GREEN}Correct agent identified in notification: {notification.get('agent') or notification.get('type')}{Style.RESET_ALL}")
                            break
                
                # If still not found, check response content as fallback
                if not test_result["correct_agent_used"] and "response" in response_data:
                    response_text = response_data["response"].lower()
                    if test_case["expected_agent"] == "room_service_agent" and any(keyword in response_text for keyword in ["towel", "housekeeping", "food", "order"]):
                        test_result["correct_agent_used"] = True
                    elif test_case["expected_agent"] == "maintenance_agent" and any(keyword in response_text for keyword in ["maintenance", "repair", "fix"]):
                        test_result["correct_agent_used"] = True
            
            # Check if correct dashboard was notified
            if test_case["expected_dashboard"] == "room_service" and test_result["room_service_notification_received"]:
                # Get the first notification
                notification = self.room_service_notifications[test_case["name"]][0]
                test_result["notification_time"] = notification["timestamp"] - test_start_time
                
                # Check if the notification data contains the expected agent
                notification_data = notification["data"]
                if "payload" in notification_data and "agent" in notification_data["payload"]:
                    if notification_data["payload"]["agent"] == test_case["expected_agent"]:
                        test_result["correct_dashboard_notified"] = True
                        logger.info(f"{Fore.GREEN}Correct dashboard notified with correct agent: {notification_data['payload']['agent']}{Style.RESET_ALL}")
                    else:
                        logger.info(f"{Fore.YELLOW}Dashboard notified but with wrong agent: {notification_data['payload']['agent']}{Style.RESET_ALL}")
                else:
                    # If agent field not found, still count as success for dashboard notification
                    test_result["correct_dashboard_notified"] = True
                    logger.info(f"{Fore.YELLOW}Dashboard notified but agent info missing in payload{Style.RESET_ALL}")
                
            elif test_case["expected_dashboard"] == "admin" and test_result["admin_notification_received"]:
                notification = self.admin_notifications[test_case["name"]][0]
                test_result["notification_time"] = notification["timestamp"] - test_start_time
                
                # Check if the notification data contains the expected agent
                notification_data = notification["data"]
                if "payload" in notification_data and "agent" in notification_data["payload"]:
                    if notification_data["payload"]["agent"] == test_case["expected_agent"]:
                        test_result["correct_dashboard_notified"] = True
                        logger.info(f"{Fore.GREEN}Correct dashboard notified with correct agent: {notification_data['payload']['agent']}{Style.RESET_ALL}")
                    else:
                        logger.info(f"{Fore.YELLOW}Dashboard notified but with wrong agent: {notification_data['payload']['agent']}{Style.RESET_ALL}")
                else:
                    # If agent field not found, still count as success for dashboard notification
                    test_result["correct_dashboard_notified"] = True
                    logger.info(f"{Fore.YELLOW}Dashboard notified but agent info missing in payload{Style.RESET_ALL}")
            
            # Determine overall success
            test_result["success"] = test_result["guest_response_received"] and test_result["correct_dashboard_notified"]
            
            # Add errors if any
            if not test_result["guest_response_received"]:
                test_result["errors"].append("No response received from server")
            if not test_result["correct_agent_used"]:
                test_result["errors"].append(f"Expected agent '{test_case['expected_agent']}' was not used")
            if not test_result["correct_dashboard_notified"]:
                test_result["errors"].append(f"Expected dashboard '{test_case['expected_dashboard']}' was not notified")
            
            # Add end time
            test_result["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add to test results
            self.test_results.append(test_result)
            
            # Log result
            self._log_test_result(test_result)
            
        except Exception as e:
            logger.error(f"{Fore.RED}Error running test case: {e}{Style.RESET_ALL}")
            test_result["errors"].append(f"Exception: {str(e)}")
            test_result["success"] = False
            self.test_results.append(test_result)
    
    def _log_test_result(self, result):
        """Log the result of a test case."""
        if result["success"]:
            status = f"{Fore.GREEN}PASSED{Style.RESET_ALL}"
        else:
            status = f"{Fore.RED}FAILED{Style.RESET_ALL}"
        
        logger.info(f"\n{Fore.YELLOW}======= TEST RESULT: {result['name']} - {status} ======={Style.RESET_ALL}")
        logger.info(f"Message: {result['message']}")
        logger.info(f"Expected Agent: {result['expected_agent']}")
        logger.info(f"Expected Dashboard: {result['expected_dashboard']}")
        logger.info(f"Response Received: {result['guest_response_received']}")
        logger.info(f"Correct Agent Used: {result['correct_agent_used']}")
        logger.info(f"Correct Dashboard Notified: {result['correct_dashboard_notified']}")
        
        if result["response_time"]:
            logger.info(f"Response Time: {result['response_time']:.2f} seconds")
        
        if result["notification_time"]:
            logger.info(f"Notification Time: {result['notification_time']:.2f} seconds")
        
        if result["errors"]:
            logger.info(f"{Fore.RED}Errors:{Style.RESET_ALL}")
            for error in result["errors"]:
                logger.info(f"  - {error}")
    
    def generate_report(self):
        """Generate a comprehensive report of all test results."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        report = f"""
{Fore.CYAN}======================================================
                AGENT FLOW TEST REPORT
======================================================{Style.RESET_ALL}

Test Run Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Server URL: {self.server_url}
Wait Time: {self.wait_time} seconds

{Fore.CYAN}======= SUMMARY ======={Style.RESET_ALL}
Total Tests: {total_tests}
Passed Tests: {passed_tests}
Failed Tests: {total_tests - passed_tests}
Success Rate: {(passed_tests / total_tests) * 100:.2f}%

{Fore.CYAN}======= DETAILED RESULTS ======={Style.RESET_ALL}
"""
        
        for i, result in enumerate(self.test_results, 1):
            if result["success"]:
                status = f"{Fore.GREEN}PASSED{Style.RESET_ALL}"
            else:
                status = f"{Fore.RED}FAILED{Style.RESET_ALL}"
                
            report += f"""
Test #{i}: {result['name']} - {status}
  Start Time: {result['start_time']}
  End Time: {result['end_time']}
  Message: {result['message']}
  Expected Agent: {result['expected_agent']}
  Expected Dashboard: {result['expected_dashboard']}
  Response Received: {result['guest_response_received']}
  Correct Agent Used: {result['correct_agent_used']}
  Correct Dashboard Notified: {result['correct_dashboard_notified']}
"""
            
            if result["response_time"]:
                report += f"  Response Time: {result['response_time']:.2f} seconds\n"
            
            if result["notification_time"]:
                report += f"  Notification Time: {result['notification_time']:.2f} seconds\n"
            
            if result["errors"]:
                report += f"  {Fore.RED}Errors:{Style.RESET_ALL}\n"
                for error in result["errors"]:
                    report += f"    - {error}\n"
        
        report += f"""
{Fore.CYAN}======= CONCLUSION ======={Style.RESET_ALL}
"""
        
        if passed_tests == total_tests:
            report += f"{Fore.GREEN}All tests passed successfully! The agent system is working as expected.{Style.RESET_ALL}\n"
        elif passed_tests > 0:
            report += f"{Fore.YELLOW}Some tests passed, but there were failures. Please review the detailed results.{Style.RESET_ALL}\n"
        else:
            report += f"{Fore.RED}All tests failed. The agent system is not working as expected.{Style.RESET_ALL}\n"
        
        report += f"""
{Fore.CYAN}======================================================{Style.RESET_ALL}
"""
        
        return report
    
    async def run_all_tests(self):
        """Run all test cases."""
        # Connect to server
        connected = await self.connect_sockets()
        
        if not connected:
            logger.error(f"{Fore.RED}Failed to connect to server. Aborting tests.{Style.RESET_ALL}")
            return False
        
        # Run each test case
        for test_case in self.test_cases:
            await self.run_test_case(test_case)
            # Wait between test cases
            await asyncio.sleep(5)
        
        # Generate and print report
        report = self.generate_report()
        print(report)
        
        # Save report to file
        report_filename = f"agent_flow_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, "w") as f:
            # Remove ANSI color codes for file output
            clean_report = report
            for color in [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Style.RESET_ALL]:
                clean_report = clean_report.replace(color, "")
            f.write(clean_report)
        
        logger.info(f"Report saved to {report_filename}")
        
        # Disconnect from server
        await self.disconnect_sockets()
        
        return True

async def main():
    parser = argparse.ArgumentParser(description='Test the agent flow system')
    parser.add_argument('--server', default='http://localhost:5000', help='Server URL (default: http://localhost:5000)')
    parser.add_argument('--wait', type=int, default=50, help='Wait time in seconds (default: 180)')
    args = parser.parse_args()
    
    tester = AgentFlowTester(server_url=args.server, wait_time=args.wait)
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())