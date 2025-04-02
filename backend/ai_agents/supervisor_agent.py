from typing import List, Dict, Any, Optional, Tuple
import torch
import asyncio
from pydantic import BaseModel, Field
from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt import create_react_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from .base_agent import BaseAgent, AgentOutput

class LlamaWrapper(BaseChatModel):
    """Wrapper to make LlamaForCausalLM work with LangGraph."""
    
    model: Any = None
    tokenizer: Any = None
    device: Any = None
    
    def __init__(self, model, tokenizer, device):
        super().__init__()
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> str:
        try:
            # Convert messages to prompt
            prompt = ""
            for message in messages:
                if isinstance(message, HumanMessage):
                    prompt += f"Human: {message.content}\n"
                elif isinstance(message, AIMessage):
                    prompt += f"Assistant: {message.content}\n"
            prompt += "Assistant: "  # Add prefix for response
                
            # Generate response using local model
            inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(self.device)
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs["input_ids"],
                    max_new_tokens=512,  # Limit response length
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
            return response.strip()
            
        except Exception as e:
            print(f"Error in _generate: {str(e)}")
            return "I apologize, but I encountered an error processing your request."
        
    def _llm_type(self) -> str:
        return "llama_wrapper"
        
    def bind_tools(self, tools, **kwargs):
        """
        Implement bind_tools method required by BaseChatModel.
        This is a simple implementation that just returns self since we're handling tools manually.
        """
        # Just return self since we're not actually binding tools in the traditional sense
        return self

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
        # First, check for room service related keywords for direct handling
        message_lower = message.lower()
        if any(keyword in message_lower for keyword in
              ["towel", "room service", "food", "order", "burger", "fries",
               "breakfast", "lunch", "dinner", "meal"]):
            # Directly return room service agent if available
            room_service_agent = next(
                (agent for agent in self.agents.values() if agent.name == "room_service_agent"),
                None
            )
            if room_service_agent:
                return room_service_agent
        
        # Fallback to normal agent selection for other messages
        eligible_agents = [
            agent for agent in self.agents.values()
            if agent.should_handle(message, history)
        ]
        
        if not eligible_agents:
            # If no agent is eligible but contains room-related keywords, default to room service
            if "room" in message_lower and any(service in message_lower for service in
                                               ["service", "need", "want", "help"]):
                return next(
                    (agent for agent in self.agents.values() if agent.name == "room_service_agent"),
                    None
                )
            return None
            
        # Return the highest priority eligible agent
        return max(eligible_agents, key=lambda x: x.priority)
    
    def build_workflow(self) -> Graph:
        """Build the LangGraph workflow for agent coordination."""
        
        # Create chat model wrapper
        chat_model = LlamaWrapper(self.model, self.tokenizer, self.device)
        
        # Create nodes for each agent
        agent_nodes = {}
        for agent_name, agent in self.agents.items():
            # Get tool definitions
            tool_definitions = agent.get_available_tools()
            
            # Create tool implementations
            tools = {}
            for tool_def in tool_definitions:
                # Create a properly named function for each tool
                tool_name = tool_def["function"]["name"]
                
                async def tool_impl(inputs: Dict[str, Any], tool_name=tool_name, agent=agent):
                    """Generic tool implementation that delegates to agent."""
                    return await agent.handle_tool_call(tool_name, inputs)
                
                # Set the tool name and __name__ attribute
                tool_impl.__name__ = tool_name
                tools[tool_name] = tool_impl
            
            # Create the agent node with wrapped model
            agent_node = create_react_agent(
                model=chat_model,
                tools=list(tools.values()),
                name=agent_name
            )
            agent_nodes[agent_name] = agent_node
        
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
        
        # Add an end node that properly returns the state
        def end_node(state: SupervisorState) -> SupervisorState:
            # Simply return the state unchanged
            return state
            
        workflow.add_node("end", end_node)
        
        for agent_name, agent_node in agent_nodes.items():
            workflow.add_node(agent_name, agent_node)
            
        # Connect nodes
        # Set the entry point
        workflow.set_entry_point("route")
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
        
        try:
            # Special handling for room service requests to ensure they work even if model fails
            message_lower = message.lower()
            if any(keyword in message_lower for keyword in
                  ["towel", "room service", "food", "order", "burger", "fries"]):
                room_service_agent = next(
                    (agent for agent in self.agents.values() if agent.name == "room_service_agent"),
                    None
                )
                if room_service_agent:
                    # Process directly with room service agent
                    response = room_service_agent.process(message, history)
                    
                    # Handle async response if needed
                    if asyncio.iscoroutine(response):
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            response = loop.run_until_complete(response)
                        finally:
                            loop.close()
                    
                    # Ensure response has agent info
                    if not any(n.get('agent') == 'room_service_agent' for n in response.notifications):
                        response.notifications.append({
                            'agent': 'room_service_agent',
                            'type': 'agent_info'
                        })
                        
                    return response
            
            # Run the workflow for other requests
            final_state = self.workflow.invoke(state)
            
            # Extract the final response
            if final_state.current_agent:
                agent = self.agents[final_state.current_agent]
                # Process directly with the agent, bypassing the workflow
                response = agent.process(message, history)
                
                # Handle async response if needed
                if asyncio.iscoroutine(response):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        response = loop.run_until_complete(response)
                    finally:
                        loop.close()
                
                # Add agent name to response if missing
                if not any(n.get('agent') == agent.name for n in response.notifications):
                    response.notifications.append({
                        'agent': agent.name,
                        'type': 'agent_info'
                    })
                        
                return response
            else:
                return AgentOutput(
                    response="I'm not sure how to help with that request."
                )
        except Exception as e:
            return AgentOutput(
                response="I apologize, but I encountered an error processing your request. Please try again.",
                notifications=[{
                    "type": "error",
                    "severity": "error",
                    "message": str(e)
                }]
            )