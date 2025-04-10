from typing import List, Dict, Any
from .base_agent import BaseAgent, AgentOutput

class SupervisorAgent(BaseAgent):
    def __init__(self, name: str, model, tokenizer):
        super().__init__(name, model, tokenizer)
        self.agents = []
        self.agent_keyword_map = {}

    def register_agent(self, agent: BaseAgent):
        self.agents.append(agent)
        keywords = agent.get_keywords()
        for keyword in keywords:
            self.agent_keyword_map[keyword] = agent

    def should_handle(self, message: str) -> bool:
        return True  # SupervisorAgent handles all messages

    def process(self, message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        selected_agent = self._select_next_agent(message, history)
        if selected_agent:
            return selected_agent.process(message, history)
        else:
            return self._generate_default_response(message)

    def _select_next_agent(self, message: str, history: List[Dict[str, str]]) -> BaseAgent:
        # Check for direct keyword matches
        for keyword, agent in self.agent_keyword_map.items():
            if keyword.lower() in message.lower():
                return agent

        # If no keyword match, check which agents can handle the message
        capable_agents = [agent for agent in self.agents if agent.should_handle(message)]
        if capable_agents:
            return max(capable_agents, key=lambda a: a.priority)

        return None

    def _generate_default_response(self, message: str) -> Dict[str, Any]:
        system_prompt = (
            "You are an AI assistant for a hotel. "
            "Respond to guests politely and efficiently. "
            "Keep responses concise and professional."
        )

        response = self.generate_response(message, system_prompt)
        return self.format_output(response)

    def get_keywords(self) -> List[str]:
        return []  # SupervisorAgent doesn't have specific keywords