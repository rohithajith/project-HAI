"""
aim of the agent: Routes requests to appropriate agents.
inputs of agent: User message, conversation history.
output json of the agent: Response from the selected agent.
method: Uses keyword matching to select agents.
"""
from typing import List, Dict, Any
from .base_agent import BaseAgent, AgentOutput, ToolDefinition
from .rag_utils import rag_helper
import re

class SupervisorAgent(BaseAgent):
    def __init__(self, name: str, model, tokenizer):
        super().__init__(name, model, tokenizer)
        self.agents = []
        self.priority = 10  # Highest priority as a routing agent

    def register_agent(self, agent: BaseAgent):
        if agent not in self.agents:
            self.agents.append(agent)

    def get_available_tools(self) -> List[ToolDefinition]:
        """Define available tools for the SupervisorAgent"""
        return [
            ToolDefinition(
                name="route_request", 
                description="Route a request to the most appropriate agent based on message content"
            ),
            ToolDefinition(
                name="list_available_agents", 
                description="List all registered agents and their capabilities"
            )
        ]

    def handle_tool_call(self, tool_name: str, **kwargs) -> Any:
        """Handle specific tool calls for the SupervisorAgent"""
        if tool_name == "route_request":
            message = kwargs.get('message', '')
            system_prompt = (
                "You are a router AI. Given the following list of agents and a message, decide which agent is best suited to handle the message.\n"
                "Return only the name of the best-suited agent."
            )
            agent_names = [agent.name for agent in self.agents]
            prompt = f"Available agents: {', '.join(agent_names)}\nMessage: {message}\nAgent to handle:"
            selected_agent_name = self.generate_response(prompt, None, system_prompt).strip()
            selected_agent = next((agent for agent in self.agents if agent.name == selected_agent_name), None)
            if selected_agent:
                return {
                    "selected_agent": selected_agent.name
                }
            return {"error": "No suitable agent found"}
        
        elif tool_name == "list_available_agents":
            return {
                "agents": [
                    {
                        "name": agent.name, 
                        "priority": getattr(agent, 'priority', 0)
                    } for agent in self.agents
                ]
            }
        
        raise NotImplementedError(f"Tool '{tool_name}' not implemented for SupervisorAgent")

    def should_handle(self, message: str) -> bool:
        return True  # Always handle for routing decision
    
    def process(self, message: str, memory) -> Dict[str, Any]:
        agent_names = [agent.name for agent in self.agents]
        system_prompt = self.load_prompt("supervisor_prompt.txt", context=', '.join(agent_names))
        prompt = f"Message: {message}\nAgent to handle:"
        selected_agent_name = self.generate_response(prompt, memory, system_prompt).strip()
        selected_agent = next((agent for agent in self.agents if agent.name == selected_agent_name), None)
        if selected_agent:
            response = selected_agent.process(message, memory)
            # Ensure the response includes the routing information
            response['agent'] = selected_agent.name
            response['tool_calls'] = response.get('tool_calls', []) + [
                {
                    "tool_name": "route_request",
                    "parameters": {
                        "message": message,
                        "selected_agent": selected_agent.name
                    }
                }
            ]
            return response
        else:
            return self._generate_default_response(message, memory)

    def _generate_default_response(self, message: str, memory) -> Dict[str, Any]:
        # More generic, helpful default response
        system_prompt = self.load_prompt("supervisor_default_prompt.txt")

        # Generate a friendly, helpful response
        response = self.generate_response(message, memory, system_prompt)
        return self.format_output(response, agent_name="SupervisorAgent")

    def get_keywords(self) -> List[str]:
        return []  # SupervisorAgent doesn't have specific keywords