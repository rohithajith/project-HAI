import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any
from .base_agent import BaseAgent, AgentOutput, ToolDefinition

class MaintenanceAgent(BaseAgent):
    def __init__(self, name: str, model, tokenizer):
        super().__init__(name, model, tokenizer)
        self.priority = 2
        self.notifications = []

    def should_handle(self, message: str) -> bool:
        keywords = ["broken", "repair", "fix", "not working", "schedule maintenance"]
        return any(keyword in message.lower() for keyword in keywords)

    def process(self, message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        system_prompt = (
            "You are an AI assistant for hotel maintenance. "
            "Respond to guests politely and efficiently regarding maintenance issues. "
            "Keep responses concise and professional."
        )

        response = self.generate_response(message, system_prompt)

        # Determine the issue type
        if "broken" in message.lower():
            issue_type = "repair"
        elif "not working" in message.lower():
            issue_type = "malfunction"
        else:
            issue_type = "general maintenance"

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
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": self.name
        })

        return self.format_output(response, [notification])

    def get_available_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition("report_issue", "Report a maintenance issue"),
            ToolDefinition("schedule_maintenance", "Schedule a maintenance appointment")
        ]

    def handle_tool_call(self, tool_name: str, **kwargs) -> Any:
        if tool_name == "report_issue":
            # Implement issue reporting logic here
            return {"issue_id": "M12345", "status": "reported"}
        elif tool_name == "schedule_maintenance":
            # Implement maintenance scheduling logic here
            return {"appointment_id": "A67890", "status": "scheduled"}
        else:
            return super().handle_tool_call(tool_name, **kwargs)

    def get_keywords(self) -> List[str]:
        return ["broken", "repair", "fix", "not working", "schedule maintenance"]

    def _save_to_log(self, data: Dict[str, Any]):
        log_dir = os.path.join("logs", "maintenance")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"maintenance_log_{datetime.now().strftime('%Y%m%d')}.json")
        
        with open(log_file, "a") as f:
            json.dump(data, f)
            f.write("\n")