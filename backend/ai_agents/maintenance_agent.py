"""
aim of the agent: Handles maintenance requests and schedules repairs.
inputs of agent: User message, issue description.
output json of the agent: Maintenance request confirmation or status.
method: Logs issues and notifies maintenance staff.
"""
import json
import os
import re
from datetime import datetime, timezone
from typing import List, Dict, Any
from .base_agent import BaseAgent, AgentOutput, ToolDefinition
from .rag_utils import rag_helper

class MaintenanceAgent(BaseAgent):
    def __init__(self, name: str, model, tokenizer):
        super().__init__(name, model, tokenizer)
        self.priority = 2
        self.notifications = []

    def should_handle(self, message: str) -> bool:
        keywords = ["broken", "repair", "fix", "not working", "schedule maintenance"]
        return any(keyword in message.lower() for keyword in keywords)

    def process(self, message: str, memory) -> Dict[str, Any]:
        # Get only highly relevant lines with a higher threshold
        relevant_lines = rag_helper.get_relevant_passages(message, min_score=0.5, k=5)
        
        # Only include context if we found relevant information
        if relevant_lines:
            # Format the relevant information in a clean, structured way
            formatted_context = ""
            for passage, score in relevant_lines:
                if score > 0.5:  # Only include highly relevant information
                    formatted_context += f"• {passage.strip()}\n"
            
            system_prompt = (
                "You are an AI assistant for hotel maintenance. "
                f"The guest has reported: '{message}'\n"
                "Answer ONLY using these specific details if relevant:\n"
                f"{formatted_context}\n"
                "Be concise and professional. Assure them that their maintenance issue "
                "will be addressed promptly by our maintenance team."
            )
        else:
            # No relevant information found, use a generic prompt
            system_prompt = (
                "You are an AI assistant for hotel maintenance. "
                "Respond to guests politely and efficiently regarding maintenance issues. "
                "Keep responses concise and professional. "
                "Assure them that their maintenance issue will be addressed promptly by our maintenance team."
            )

        response = self.generate_response(message, memory, system_prompt)

        # Prepare tool calls
        tool_calls = []

        # Determine the issue type and create appropriate tool calls
        if "broken" in message.lower():
            issue_type = "repair"
            tool_calls.append({
                "tool_name": "report_issue",
                "parameters": {
                    "issue_type": "repair",
                    "description": message
                }
            })
        elif "not working" in message.lower():
            issue_type = "malfunction"
            tool_calls.append({
                "tool_name": "report_issue",
                "parameters": {
                    "issue_type": "malfunction",
                    "description": message
                }
            })
        else:
            issue_type = "general maintenance"
            tool_calls.append({
                "tool_name": "schedule_maintenance",
                "parameters": {
                    "issue_type": "general maintenance",
                    "description": message
                }
            })

        # If no specific tool calls were generated, add a generic check
        if not tool_calls:
            tool_calls.append({
                "tool_name": "check_maintenance_status",
                "parameters": {}
            })

        # Create a notification
        notification = {
            "type": "maintenance_request",
            "issue_type": issue_type,
            "description": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": self.name
        }
        self.notifications.append(notification)

        # Save the structured output to a log file
        self._save_to_log({
            "input": message,
            "response": response,
            "notification": notification,
            "tool_calls": tool_calls,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": self.name
        })

        return self.format_output(response, tool_calls)

    def get_available_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition("report_issue", "Report a maintenance issue"),
            ToolDefinition("schedule_maintenance", "Schedule a maintenance appointment"),
            ToolDefinition("check_maintenance_status", "Check the status of maintenance requests")
        ]

    def handle_tool_call(self, tool_name: str, **kwargs) -> Any:
        if tool_name == "report_issue":
            # Implement issue reporting logic here
            issue_details = {
                "issue_id": f"MAINT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "status": "reported",
                "issue_type": kwargs.get('issue_type', 'unspecified'),
                "description": kwargs.get('description', '')
            }
            return issue_details
        elif tool_name == "schedule_maintenance":
            # Implement maintenance scheduling logic here
            appointment_details = {
                "appointment_id": f"APPT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "status": "scheduled",
                "issue_type": kwargs.get('issue_type', 'general maintenance'),
                "description": kwargs.get('description', '')
            }
            return appointment_details
        elif tool_name == "check_maintenance_status":
            # Implement maintenance status check logic
            return {
                "status": "no_active_requests",
                "message": "No current maintenance requests found."
            }
        else:
            return super().handle_tool_call(tool_name, **kwargs)

    def get_keywords(self) -> List[str]:
        return ["broken", "repair", "fix", "not working", "schedule maintenance"]

    def _save_to_log(self, data: Dict[str, Any]):
        log_dir = os.path.join("logs", "maintenance")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"maintenance_log_{datetime.now().strftime('%Y%m%d')}.jsonl")
        
        with open(log_file, "a") as f:
            json.dump(data, f)
            f.write("\n")