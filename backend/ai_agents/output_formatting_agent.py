import json
import logging
from typing import Dict, Any, Union

class OutputFormattingAgent:
    def __init__(self):
        """
        Initialize the Output Formatting Agent
        Responsible for converting AI agent outputs to multiple formats
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def format_response(self, 
                        raw_response: Union[str, Dict[str, Any]], 
                        request_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Convert raw agent response to standardized output formats

        Args:
            raw_response (Union[str, Dict]): Original agent response
            request_context (Dict, optional): Context of the original request

        Returns:
            Dict containing both JSON and human-readable formats
        """
        try:
            # If input is already a dictionary, use it directly
            if isinstance(raw_response, dict):
                processed_response = raw_response
            # If input is a string, attempt to parse or use as is
            elif isinstance(raw_response, str):
                try:
                    processed_response = json.loads(raw_response)
                except json.JSONDecodeError:
                    processed_response = {"response": raw_response}
            else:
                processed_response = {"response": str(raw_response)}

            # Ensure standard keys
            formatted_response = {
                "json_output": processed_response,
                "human_output": self._generate_human_readable(processed_response),
                "metadata": {
                    "timestamp": self._get_current_timestamp(),
                    "request_context": request_context or {}
                }
            }

            return formatted_response

        except Exception as e:
            self.logger.error(f"Error in output formatting: {e}")
            return {
                "json_output": {"error": str(e)},
                "human_output": "Sorry, there was an error processing the response.",
                "metadata": {
                    "timestamp": self._get_current_timestamp(),
                    "error": str(e)
                }
            }

    def _generate_human_readable(self, response: Dict[str, Any]) -> str:
        """
        Generate a human-friendly version of the response

        Args:
            response (Dict): Processed response dictionary

        Returns:
            str: Human-readable output
        """
        if isinstance(response, dict):
            # Handle different response types
            if 'response' in response:
                return response['response']
            elif 'message' in response:
                return response['message']
            elif 'result' in response:
                return str(response['result'])
            else:
                return " ".join([f"{k}: {v}" for k, v in response.items()])
        return str(response)

    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp

        Returns:
            str: ISO format timestamp
        """
        from datetime import datetime
        return datetime.now().isoformat()

    def process_notification(self, 
                             notification_type: str, 
                             room_number: str, 
                             additional_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a standardized notification

        Args:
            notification_type (str): Type of notification
            room_number (str): Room number associated with notification
            additional_info (Dict, optional): Extra details about notification

        Returns:
            Dict with notification details
        """
        notification = {
            "type": notification_type,
            "room_number": room_number,
            "timestamp": self._get_current_timestamp(),
            "agent": "output_formatting_agent"
        }

        if additional_info:
            notification.update(additional_info)

        return self.format_response(notification)

# Singleton instance for easy import and use
output_formatter = OutputFormattingAgent()