from typing import List, Dict, Any
from .base_agent import BaseAgent, AgentOutput
from .rag_utils import rag_helper

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

    def process(self, message: str, memory) -> Dict[str, Any]:
        selected_agent = self._select_next_agent(message, memory)
        if selected_agent:
            return selected_agent.process(message, memory)
        else:
            return self._generate_default_response(message, memory)

    def _select_next_agent(self, message: str, memory) -> BaseAgent:
        # Check for direct keyword matches
        for keyword, agent in self.agent_keyword_map.items():
            if keyword.lower() in message.lower():
                return agent

        # If no keyword match, check which agents can handle the message
        capable_agents = [agent for agent in self.agents if agent.should_handle(message)]
        if capable_agents:
            return max(capable_agents, key=lambda a: a.priority)

        return None

    def _generate_default_response(self, message: str, memory) -> Dict[str, Any]:
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
                "You are an AI assistant for a hotel. "
                f"The guest has asked: '{message}'\n"
                "Answer ONLY using these specific details:\n"
                f"{formatted_context}\n"
                "Be concise and professional. If you don't have enough information to fully "
                "answer their question, offer to connect them with the appropriate hotel staff."
            )
        else:
            # No relevant information found, use a generic prompt
            system_prompt = (
                "You are an AI assistant for a hotel. "
                "Respond to guests politely and efficiently. "
                "Keep responses concise and professional. "
                "Offer to connect them with hotel staff for detailed information."
            )

        response = self.generate_response(message, memory, system_prompt)
        return self.format_output(response)

    def get_keywords(self) -> List[str]:
        return []  # SupervisorAgent doesn't have specific keywords