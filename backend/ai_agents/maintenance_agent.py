"""
aim of the agent: Handles maintenance requests and schedules repairs.
inputs of agent: User message, issue description.
output json of the agent: Maintenance request confirmation or status.
method: Logs issues and notifies maintenance staff using LangChain tools.
"""
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any

from langchain.tools import tool
from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field

from .base_agent import BaseAgent, AgentOutput, LangChainToolWrapper
from .rag_utils import rag_helper
from .local_llm import LocalLLM

class MaintenanceIssueInput(BaseModel):
    """Input model for maintenance issue reporting."""
    issue_type: str = Field(..., description="Type of maintenance issue")
    description: str = Field(..., description="Detailed description of the issue")

class MaintenanceAgent(BaseAgent):
    def __init__(self, name: str, model, tokenizer):
        super().__init__(name, model, tokenizer)
        self.description = "Handles maintenance requests, identifies issue types, and schedules repairs or checks status based on guest reports."
        self.system_prompt = "You are an AI hotel maintenance assistant. Help guests by reporting or scheduling fixes for broken or malfunctioning equipment."
        self.priority = 2
        self.notifications = []
        self.local_llm = LocalLLM(model, tokenizer)

    def should_handle(self, message: str) -> bool:
        keywords = ["broken", "repair", "fix", "not working", "schedule maintenance"]
        return any(keyword in message.lower() for keyword in keywords)

    def get_available_tools(self) -> List[BaseTool]:
        """
        Returns LangChain-compatible tools for the agent.
        
        Returns:
            List of BaseTool instances
        """
        return [
            LangChainToolWrapper.wrap_tool(
                self.report_issue, 
                "report_maintenance_issue", 
                "Report a specific maintenance issue in the hotel"
            ),
            LangChainToolWrapper.wrap_tool(
                self.schedule_maintenance, 
                "schedule_maintenance_appointment", 
                "Schedule a maintenance appointment for a specific issue"
            ),
            LangChainToolWrapper.wrap_tool(
                self.check_maintenance_status, 
                "check_maintenance_status", 
                "Check the current status of maintenance requests"
            )
        ]

    def process(self, message: str, memory) -> Dict[str, Any]:
        # Existing RAG and response generation logic remains the same
        relevant_lines = rag_helper.get_relevant_passages(message, min_score=0.5, k=5)
        
        system_prompt = self._generate_system_prompt(message, relevant_lines)
        response = self.generate_response(message, memory, system_prompt)

        # Determine and create tool calls
        tool_calls = self._generate_tool_calls(message)

        # Create and save notification
        notification = self._create_notification(message, tool_calls)
        self._save_to_log({
            "input": message,
            "response": response,
            "notification": notification,
            "tool_calls": tool_calls,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": self.name
        })

        return self.format_output(response, tool_calls)

    def _generate_system_prompt(self, message: str, relevant_lines: List[tuple]) -> str:
        """Generate a context-aware system prompt."""
        if relevant_lines:
            formatted_context = "\n".join([
                f"• {passage.strip()}" for passage, score in relevant_lines if score > 0.5
            ])
            return (
                "You are an AI assistant for hotel maintenance. "
                f"The guest has reported: '{message}'\n"
                "Answer ONLY using these specific details if relevant:\n"
                f"{formatted_context}\n"
                "Be concise and professional. Assure them that their maintenance issue "
                "will be addressed promptly by our maintenance team."
            )
        else:
            return (
                "You are an AI assistant for hotel maintenance. "
                "Respond to guests politely and efficiently regarding maintenance issues. "
                "Keep responses concise and professional. "
                "Assure them that their maintenance issue will be addressed promptly by our maintenance team."
            )

    def _generate_tool_calls(self, message: str) -> List[Dict[str, Any]]:
        """Generate appropriate tool calls based on message content."""
        tool_calls = []
        
        if "broken" in message.lower():
            tool_calls.append({
                "tool_name": "report_maintenance_issue",
                "parameters": {
                    "issue_type": "repair",
                    "description": message
                }
            })
        elif "not working" in message.lower():
            tool_calls.append({
                "tool_name": "report_maintenance_issue",
                "parameters": {
                    "issue_type": "malfunction",
                    "description": message
                }
            })
        else:
            tool_calls.append({
                "tool_name": "schedule_maintenance_appointment",
                "parameters": {
                    "issue_type": "general maintenance",
                    "description": message
                }
            })

        # Fallback if no specific tool calls
        if not tool_calls:
            tool_calls.append({
                "tool_name": "check_maintenance_status",
                "parameters": {}
            })

        return tool_calls

    def _create_notification(self, message: str, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a notification dictionary."""
        issue_type = tool_calls[0].get('parameters', {}).get('issue_type', 'general')
        return {
            "type": "maintenance_request",
            "issue_type": issue_type,
            "description": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": self.name
        }

    @tool
    def report_issue(self, issue_type: str, description: str) -> Dict[str, Any]:
        """
        LangChain tool to report a maintenance issue.
        
        Args:
            issue_type (str): Type of maintenance issue
            description (str): Detailed description of the issue
        
        Returns:
            Dict with issue details and status
        """
        issue_details = {
            "issue_id": f"MAINT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "reported",
            "issue_type": issue_type or 'unspecified',
            "description": description,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        return issue_details

    @tool
    def schedule_maintenance(self, issue_type: str, description: str) -> Dict[str, Any]:
        """
        LangChain tool to schedule a maintenance appointment.
        
        Args:
            issue_type (str): Type of maintenance needed
            description (str): Details about the maintenance requirement
        
        Returns:
            Dict with appointment details and status
        """
        appointment_details = {
            "appointment_id": f"APPT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "scheduled",
            "issue_type": issue_type or 'general maintenance',
            "description": description,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        return appointment_details

    @tool
    def check_maintenance_status(self) -> Dict[str, str]:
        """
        LangChain tool to check maintenance request status.
        
        Returns:
            Dict with maintenance request status
        """
        return {
            "status": "no_active_requests",
            "message": "No current maintenance requests found."
        }

    def _save_to_log(self, data: Dict[str, Any]):
        """Save maintenance logs to a file."""
        log_dir = os.path.join("logs", "maintenance")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"maintenance_log_{datetime.now().strftime('%Y%m%d')}.jsonl")
        
        with open(log_file, "a") as f:
            json.dump(data, f)
            f.write("\n")

    def get_keywords(self) -> List[str]:
        return ["broken", "repair", "fix", "not working", "schedule maintenance"]