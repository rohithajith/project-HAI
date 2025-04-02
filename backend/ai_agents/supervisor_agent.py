from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt import create_react_agent
from .base_agent import BaseAgent, AgentOutput

class SupervisorState(BaseModel):
    """State maintained between agent calls in the workflow."""
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    current_agent: Optional[str] = None
    completed_agents: List[str] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)

class SupervisorAgent:
    """Coordinates workflow between specialized agents."""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.workflow: Optional[Graph] = None
        self.model = None
        self.tokenizer = None
        self.device = None
        
    def register_agent(self, agent: BaseAgent):
        """Register a specialized agent with the supervisor."""
        self.agents[agent.name] = agent
        
    def _select_next_agent(self, message: str, history: List[Dict[str, Any]]) -> Optional[BaseAgent]:
        """Select the most appropriate agent to handle the current message."""
        eligible_agents = [
            agent for agent in self.agents.values()
            if agent.should_handle(message, history)
        ]
        
        if not eligible_agents:
            return None
            
        # Return the highest priority eligible agent
        return max(eligible_agents, key=lambda x: x.priority)
    
    def build_workflow(self) -> Graph:
        """Build the LangGraph workflow for agent coordination."""
        
        # Create nodes for each agent
        agent_nodes = {}
        for agent in self.agents.values():
            agent_node = create_react_agent(
                model=self.model,
                tools=agent.get_available_tools(),
                name=agent.name
            )
            agent_nodes[agent.name] = agent_node
        
        # Create the graph
        workflow = StateGraph(SupervisorState)
        
        # Add agent selection logic
        def route_to_agent(state: SupervisorState) -> str:
            if not state.messages:
                return "end"
                
            message = state.messages[-1]["content"]
            history = state.messages[:-1]
            
            next_agent = self._select_next_agent(message, history)
            if not next_agent:
                return "end"
                
            state.current_agent = next_agent.name
            return next_agent.name
            
        # Add nodes and edges
        workflow.add_node("route", route_to_agent)
        for agent_name, agent_node in agent_nodes.items():
            workflow.add_node(agent_name, agent_node)
            
        # Connect nodes
        workflow.add_edge("route", "end")
        for agent_name in agent_nodes:
            workflow.add_edge("route", agent_name)
            workflow.add_edge(agent_name, "route")
            
        self.workflow = workflow.compile()
        return self.workflow
    
    def process_message(self, message: str, history: List[Dict[str, Any]]) -> AgentOutput:
        """Process a message through the agent workflow."""
        if not self.workflow:
            self.build_workflow()
            
        # Initialize state
        state = SupervisorState(
            messages=history + [{"role": "user", "content": message}]
        )
        
        # Run the workflow
        final_state = self.workflow.invoke(state)
        
        # Extract the final response
        if final_state.current_agent:
            agent = self.agents[final_state.current_agent]
            return agent.process(message, history)
        else:
            return AgentOutput(
                response="I'm not sure how to help with that request."
            )