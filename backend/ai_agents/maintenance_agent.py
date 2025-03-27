import re
from typing import List, Dict, Any, Optional

from .base_agent import BaseAgent, ToolDefinition, ToolParameters, ToolParameterProperty, AgentOutput
# Assuming a similar notification service exists in Python
# from backend.services.notification_service import notification_service

# Placeholder for the notification service if not yet implemented
class MockNotificationService:
    async def send_room_notification(self, room_number: str, message: str):
        print(f"--- NOTIFICATION to Room {room_number}: {message} ---")
    async def send_system_notification(self, notification_data: Dict[str, Any]):
         print(f"--- SYSTEM NOTIFICATION: {notification_data} ---")

notification_service = MockNotificationService() # Replace with actual import when available


class MaintenanceAgent(BaseAgent):
    name: str = "MaintenanceAgent"
    priority: int = 1 # Same priority as in JS

    tools: List[ToolDefinition] = [
        ToolDefinition(
            name='report_issue',
            description='Report a maintenance issue in the room',
            parameters=ToolParameters(
                properties={
                    'issue_type': ToolParameterProperty(
                        type='string',
                        description='Type of maintenance issue',
                        enum=['plumbing', 'electrical', 'furniture', 'appliance', 'other']
                    ),
                    'urgency': ToolParameterProperty(
                        type='string',
                        description='Urgency of the issue',
                        enum=['low', 'medium', 'high', 'emergency'],
                        default='medium'
                    ),
                    'description': ToolParameterProperty(
                        type='string',
                        description='Detailed description of the issue'
                    )
                },
                required=['issue_type', 'description'] # Making description required for clarity
            )
        ),
        ToolDefinition(
            name='schedule_maintenance',
            description='Schedule non-urgent maintenance',
            parameters=ToolParameters(
                properties={
                    'issue_type': ToolParameterProperty(
                        type='string',
                        description='Type of maintenance',
                        enum=['preventive', 'inspection', 'upgrade', 'cleaning']
                    ),
                    'preferred_time': ToolParameterProperty(
                        type='string',
                        description='Preferred time window for maintenance (e.g., "tomorrow afternoon", "Friday 9-11am")'
                    ),
                    'description': ToolParameterProperty( # Added description for clarity
                        type='string',
                        description='Brief description of the scheduled task'
                    )
                },
                required=['issue_type', 'description'] # Making description required
            )
        )
    ]

    def should_handle(self, message: str, history: List[Dict[str, Any]]) -> bool:
        """Check if the message relates to maintenance issues."""
        lower_message = message.lower()
        keywords = [
            'broken', 'repair', 'fix', 'not working', 'issue', 'problem', # report_issue triggers
            'schedule', 'maintenance', 'appointment', 'technician' # schedule_maintenance triggers
        ]
        return any(keyword in lower_message for keyword in keywords)

    async def process(self, message: str, history: List[Dict[str, Any]]) -> AgentOutput:
        """
        Process a maintenance-related request.

        This agent doesn't directly use an LLM to select tools but uses keyword matching.
        In a more advanced LangGraph setup, an LLM could be used for tool selection based on descriptions.
        For now, we mimic the JS logic.
        """
        Process a maintenance-related request using improved keyword matching.
        """
        lower_message = message.lower()
        room_number = self._extract_room_number(history) or 'unknown'
        selected_tool_name: Optional[str] = None
        tool_args: Dict[str, Any] = {}

        # More comprehensive keyword sets
        report_keywords = ['broken', 'repair', 'fix', 'not working', 'issue', 'problem', 'leak', 'leaking', 'damage', 'faulty']
        schedule_keywords = ['schedule', 'maintenance', 'appointment', 'technician', 'arrange', 'book', 'filter', 'cleaning'] # Added filter/cleaning

        is_report_request = any(k in lower_message for k in report_keywords)
        is_schedule_request = any(k in lower_message for k in schedule_keywords)

        # Prioritize reporting if both seem relevant (e.g., "schedule repair for broken sink")
        if is_report_request:
            selected_tool_name = 'report_issue'
            # Simplified arg extraction - LLM/parsing needed for real args
            # Determine issue type crudely
            issue_type = 'other'
            if any(k in lower_message for k in ['plumbing', 'leak', 'water', 'sink', 'shower', 'toilet']): issue_type = 'plumbing'
            elif any(k in lower_message for k in ['electrical', 'light', 'power', 'outlet', 'socket']): issue_type = 'electrical'
            elif any(k in lower_message for k in ['furniture', 'chair', 'table', 'bed']): issue_type = 'furniture'
            elif any(k in lower_message for k in ['appliance', 'tv', 'fridge', 'ac', 'air conditioner']): issue_type = 'appliance'

            tool_args = {'issue_type': issue_type, 'description': message, 'urgency': self._determine_urgency(message)}
            # logger.info(f"Selected tool 'report_issue' with args: {tool_args}") # Add logging if needed

        elif is_schedule_request:
            selected_tool_name = 'schedule_maintenance'
            # Simplified arg extraction
            schedule_type = 'preventive'
            if any(k in lower_message for k in ['inspection']): schedule_type = 'inspection'
            elif any(k in lower_message for k in ['upgrade']): schedule_type = 'upgrade'
            elif any(k in lower_message for k in ['cleaning', 'filter']): schedule_type = 'cleaning'
            # Crude time extraction
            preferred_time = 'any available'
            time_match = re.search(r'(tomorrow|today|friday|monday|tuesday|wednesday|thursday|weekend)\s*(morning|afternoon|evening)?', lower_message)
            if time_match:
                preferred_time = time_match.group(0)

            tool_args = {'issue_type': schedule_type, 'description': message, 'preferred_time': preferred_time}
            # logger.info(f"Selected tool 'schedule_maintenance' with args: {tool_args}") # Add logging if needed

        # Execute the selected tool if one was identified
        if selected_tool_name == 'report_issue':
            return await self._handle_issue_report(room_number, tool_args)
        elif selected_tool_name == 'schedule_maintenance':
            return await self._handle_maintenance_schedule(room_number, tool_args)
        else:
            # If should_handle was true but process didn't select a tool, return non-handling output
            return AgentOutput(response="", tool_used=False, notifications=[])

    async def _handle_issue_report(self, room_number: str, args: Dict[str, Any]) -> AgentOutput:
        """Simulates reporting the issue."""
        issue_desc = args.get('description', 'No description provided')
        urgency = args.get('urgency', 'medium')
        issue_type = args.get('issue_type', 'other')

        await notification_service.send_room_notification(
            room_number,
            f"Maintenance issue reported: {issue_desc} (Type: {issue_type}, Urgency: {urgency})"
        )
        await notification_service.send_system_notification({
             'type': 'maintenance_report',
             'roomNumber': room_number,
             'issue_type': issue_type,
             'description': issue_desc,
             'urgency': urgency
        })

        response_message = f"Your maintenance issue ('{issue_desc}') has been reported for room {room_number}. Urgency: {urgency}. A technician will address it accordingly."
        return AgentOutput(
            response=response_message,
            notifications=[{
                'event': 'maintenance_report', # Changed 'type' to 'event'
                'payload': {                   # Wrapped details in 'payload'
                    'roomNumber': room_number,
                    'issue_type': issue_type,  # Added issue_type for consistency
                    'description': issue_desc,
                    'urgency': urgency
                }
            }],
            tool_used=True,
            tool_name='report_issue',
            tool_args=args
        )

    async def _handle_maintenance_schedule(self, room_number: str, args: Dict[str, Any]) -> AgentOutput:
        """Simulates scheduling maintenance."""
        schedule_desc = args.get('description', 'No description provided')
        issue_type = args.get('issue_type', 'preventive')
        preferred_time = args.get('preferred_time', 'any available time')

        await notification_service.send_room_notification(
            room_number,
            f"Maintenance scheduled: {schedule_desc} (Type: {issue_type}, Time: {preferred_time})"
        )
        await notification_service.send_system_notification({
             'type': 'maintenance_schedule',
             'roomNumber': room_number,
             'issue_type': issue_type,
             'description': schedule_desc,
             'preferred_time': preferred_time
        })

        response_message = f"Maintenance ('{schedule_desc}') has been scheduled for room {room_number}. Preferred time: {preferred_time}. You will receive confirmation."
        return AgentOutput(
            response=response_message,
            notifications=[{
                'event': 'maintenance_schedule', # Changed 'type' to 'event'
                'payload': {                     # Wrapped details in 'payload'
                    'roomNumber': room_number,
                    'issue_type': issue_type,    # Added issue_type for consistency
                    'description': schedule_desc,
                    'preferred_time': preferred_time
                }
            }],
            tool_used=True,
            tool_name='schedule_maintenance',
            tool_args=args
        )

    def _determine_urgency(self, message: str) -> str:
        """Determines urgency based on keywords in the message."""
        lower_message = message.lower()
        if any(k in lower_message for k in ['emergency', 'urgent', 'flood', 'leak', 'fire', 'immediately']):
            return 'emergency'
        if any(k in lower_message for k in ['important', 'asap', 'soon']):
            return 'high'
        return 'medium'

# Example usage (for testing purposes)
if __name__ == '__main__':
    import asyncio

    async def test():
        agent = MaintenanceAgent()
        history = [{'role': 'user', 'content': 'I am in room 101.'}]
        message1 = "The sink in my bathroom is broken and leaking water everywhere!"
        message2 = "Can I schedule someone to come clean the air filter tomorrow afternoon?"

        print("Available tools:", agent.get_available_tools())

        print(f"\nTesting message 1: '{message1}'")
        if agent.should_handle(message1, history):
            output1 = await agent.process(message1, history)
            print("Output 1:", output1)
        else:
            print("Agent decided not to handle message 1.")

        print(f"\nTesting message 2: '{message2}'")
        if agent.should_handle(message2, history):
            output2 = await agent.process(message2, history)
            print("Output 2:", output2)
        else:
            print("Agent decided not to handle message 2.")

    asyncio.run(test())