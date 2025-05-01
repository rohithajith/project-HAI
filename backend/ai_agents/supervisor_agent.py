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
        # Use the correct path for the description file
        self.description = self.load_prompt("backend/ai_agents/descriptions/supervisor_agent_description.txt")
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
            agent_names = [agent.name for agent in self.agents]
            system_prompt = self.load_prompt("supervisor_prompt.txt", context=', '.join(agent_names))
            
            # Generate agent name from LLM
            llm_response = self.generate_response(message, None, system_prompt).strip()
            print(f"Tool call raw LLM response: {llm_response}")
            
            # Extract the agent name from the response
            selected_agent_name = self._extract_agent_name(llm_response, agent_names)
            print(f"Tool call selected agent: {selected_agent_name}")
            
            # Find the selected agent
            selected_agent = next((agent for agent in self.agents if agent.name == selected_agent_name), None)
            
            if selected_agent:
                return {
                    "selected_agent": selected_agent.name,
                    "tool_calls": [
                        {
                            "tool_name": "route_request",
                            "parameters": {
                                "message": message,
                                "selected_agent": selected_agent.name
                            }
                        }
                    ]
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
        
        # Generate agent name from LLM - the prompt now instructs the model to return just the agent name
        llm_response = self.generate_response(message, memory, system_prompt).strip()
        print(f"Raw LLM response: {llm_response}")
        
        # Extract the agent name from the response
        selected_agent_name = self._extract_agent_name(llm_response, agent_names)
        print(f"Selected agent: {selected_agent_name}")
        
        # Find the selected agent
        selected_agent = next((agent for agent in self.agents if agent.name == selected_agent_name), None)
        
        if selected_agent:
            # Process the request with the selected agent
            response = selected_agent.process(message, memory)
            
            # Add routing information to the response
            response['agent'] = selected_agent.name
            
            # Add tool calls
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
    
    def _extract_agent_name(self, response: str, agent_names: List[str]) -> str:
        """
        Extract the agent name from the LLM response.
        
        Args:
            response: The raw LLM response
            agent_names: List of valid agent names
            
        Returns:
            The extracted agent name or a default
        """
        # Clean up the response
        clean_response = response.strip()
        
        # Check if the response is exactly one of the agent names
        for agent_name in agent_names:
            if agent_name.lower() in clean_response.lower():
                return agent_name
        
        # If we can't find an exact match, look for partial matches
        for agent_name in agent_names:
            # Check for partial matches like "RoomService" instead of "RoomServiceAgent"
            if agent_name.lower().replace("agent", "") in clean_response.lower():
                return agent_name
        
        # Default to RoomServiceAgent if we can't determine the agent
        # This is a reasonable default for most hotel queries
        return "RoomServiceAgent"

    def _generate_default_response(self, message: str, memory) -> Dict[str, Any]:
        # More generic, helpful default response
        agent_names = [agent.name for agent in self.agents]
        system_prompt = self.load_prompt("supervisor_default_prompt.txt", context=', '.join(agent_names))

        # Generate agent name from LLM - the prompt now instructs the model to return just the agent name
        llm_response = self.generate_response(message, memory, system_prompt)
        print(f"Default response raw LLM response: {llm_response}")
        
        # Extract the agent name from the response
        selected_agent_name = self._extract_agent_name(llm_response, agent_names)
        print(f"Default selected agent: {selected_agent_name}")
        
        # Create a default response with the routing information
        return {
            "response": f"I'll help you with that. Let me connect you with our {selected_agent_name}.",
            "agent": "SupervisorAgent",
            "tool_calls": [
                {
                    "tool_name": "route_request",
                    "parameters": {
                        "message": message,
                        "selected_agent": selected_agent_name
                    }
                }
            ]
        }

    def get_keywords(self) -> List[str]:
        return []  # SupervisorAgent doesn't have specific keywords