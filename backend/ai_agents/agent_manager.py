import logging # Import logging
import sys # Import sys for potential stderr printing
from typing import List, Dict, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END

# Import the agents
from .base_agent import AgentOutput
from .maintenance_agent import MaintenanceAgent
from .room_service_agent import RoomServiceAgent

# Get a logger for this module
logger = logging.getLogger(__name__)

from functools import lru_cache
from datetime import datetime, timedelta

# Define the state for the graph
class AgentState(TypedDict):
    message: str
    history: List[Dict[str, Any]]
    agents: List[Any] # List of agent instances, sorted by priority
    current_agent_index: int
    final_output: Optional[AgentOutput] # Store the result from the handling agent
    agent_handled: bool # Track if any agent successfully handled the request

# --- Start of Corrected Class Definition ---
class AgentManagerCorrected:
    """
    Manages a collection of agents and processes messages through them using LangGraph.
    Uses refined node logic for clarity and implements caching for better performance.
    """
    def __init__(self, cache_ttl: int = 3600):  # Cache TTL in seconds, default 1 hour
        self.agents = sorted(
            [RoomServiceAgent(), MaintenanceAgent()],
            key=lambda agent: agent.priority,
            reverse=True
        )
        self.graph = self._build_graph()
        self.cache_ttl = cache_ttl
        self._cache = {}
        self._cache_timestamps = {}

    def _build_graph(self):
        builder = StateGraph(AgentState)
        builder.add_node("select_agent", self._select_agent_node)
        builder.add_node("run_agent", self._run_agent_node)
        builder.add_conditional_edges(
            "run_agent",
            self._decide_next_step_edge,
            {
                "continue": "select_agent",
                "end": END
            }
        )
        builder.set_entry_point("select_agent")
        return builder.compile()

    # Node Functions (bound to instance implicitly or explicitly if needed)
    def _select_agent_node(self, state: AgentState) -> AgentState:
        agent_index = state['current_agent_index']
        if agent_index >= len(state['agents']):
            # Use logger instead of print
            logger.info(f"Select: No more agents (index {agent_index}), ensuring fall-through")
            if state.get('final_output') is None: # Check if None specifically
                 state['final_output'] = AgentOutput(response="", tool_used=False, notifications=[]) # Ensure notifications list exists
        else:
            # Use logger instead of print
            logger.info(f"Select: Agent at index {agent_index} ({state['agents'][agent_index].name})")
        return state

    def _get_cache_key(self, message: str, history: List[Dict[str, Any]], agent_name: str) -> str:
        """Generate a cache key from message, last history item, and agent name."""
        last_history = history[-1]['content'] if history else ''
        return f"{agent_name}:{message}:{last_history}"

    def _get_from_cache(self, cache_key: str) -> Optional[AgentOutput]:
        """Get a cached response if it exists and hasn't expired."""
        if cache_key in self._cache:
            timestamp = self._cache_timestamps.get(cache_key)
            if timestamp and datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                logger.debug(f"Cache hit for key: {cache_key}")
                return self._cache[cache_key]
            else:
                # Clean up expired cache entry
                del self._cache[cache_key]
                del self._cache_timestamps[cache_key]
        return None

    def _add_to_cache(self, cache_key: str, output: AgentOutput):
        """Add a response to the cache."""
        self._cache[cache_key] = output
        self._cache_timestamps[cache_key] = datetime.now()
        logger.debug(f"Added to cache: {cache_key}")

    async def _run_agent_node(self, state: AgentState) -> AgentState:
        agent_index = state['current_agent_index']
        if agent_index >= len(state['agents']):
            logger.info(f"Run: Invalid index {agent_index}, skipping run")
            if state.get('final_output') is None:
                state['final_output'] = AgentOutput(
                    response="No agent available to handle the request.",
                    tool_used=False,
                    notifications=[]
                )
            return state

        agent = state['agents'][agent_index]
        message = state['message']
        history = state['history']
        
        logger.info(f"Run: Processing with agent {agent.name}")
        
        try:
            # Check cache first
            cache_key = self._get_cache_key(message, history, agent.name)
            cached_output = self._get_from_cache(cache_key)
            
            if cached_output:
                logger.info(f"Run: Using cached response for agent {agent.name}")
                state['final_output'] = cached_output
                state['agent_handled'] = True
                return state

            # Process with agent if not cached
            if agent.should_handle(message, history):
                logger.info(f"Run: Agent {agent.name} SHOULD handle")
                try:
                    output: AgentOutput = await agent.process(message, history)
                    logger.info(f"Run: Agent {agent.name} output: {output!r}")
                    
                    if output and (getattr(output, 'response', None) or getattr(output, 'tool_used', False)):
                        # Cache successful response
                        self._add_to_cache(cache_key, output)
                        state['final_output'] = output
                        state['agent_handled'] = True
                    else:
                        logger.warning(
                            f"Run: Agent {agent.name} handled but produced no actionable output.",
                            extra={'agent': agent.name, 'message': message}
                        )
                        state['final_output'] = None
                        state['agent_handled'] = False
                except Exception as e:
                    logger.error(
                        f"Run: Error during agent {agent.name} process method: {e}",
                        exc_info=True,
                        extra={'agent': agent.name, 'message': message}
                    )
                    state['final_output'] = None
                    state['agent_handled'] = False
            else:
                logger.info(f"Run: Agent {agent.name} should NOT handle")
                state['final_output'] = None
                state['agent_handled'] = False
        except Exception as e:
            logger.error(
                f"Run: Unexpected error in agent node execution: {e}",
                exc_info=True,
                extra={'agent': agent.name, 'message': message}
            )
            state['final_output'] = None
            state['agent_handled'] = False
            
        return state

    # Edge Logic
    def _decide_next_step_edge(self, state: AgentState) -> str:
        agent_output = state.get('final_output')
        current_index = state['current_agent_index']
        agent_handled = state.get('agent_handled', False)
        current_agent = state['agents'][current_index].name

        # If the current agent handled the request successfully
        if agent_handled:
            logger.info(
                f"Decide: Agent {current_agent} handled successfully. END",
                extra={'agent': current_agent, 'status': 'handled'}
            )
            return "end"
        
        # If we haven't found a handler yet, try the next agent
        next_index = current_index + 1
        if next_index < len(state['agents']):
            next_agent = state['agents'][next_index].name
            logger.info(
                f"Decide: Agent {current_agent} did not handle. Trying next agent {next_agent}",
                extra={
                    'current_agent': current_agent,
                    'next_agent': next_agent,
                    'status': 'continue'
                }
            )
            state['current_agent_index'] = next_index
            state['final_output'] = None  # Clear output before next agent
            state['agent_handled'] = False  # Reset handled flag
            return "continue"
        
        # If we've tried all agents and none handled it
        logger.warning(
            f"Decide: No agents could handle the request. Last attempted: {current_agent}",
            extra={
                'tried_agents': [agent.name for agent in state['agents']],
                'status': 'fallthrough'
            }
        )
        
        # Set a friendly fallback response
        if state.get('final_output') is None:
            state['final_output'] = AgentOutput(
                response="I apologize, but I don't have the capability to handle this request. Could you please try rephrasing or ask something else?",
                tool_used=False,
                notifications=["No agent could process this request"]
            )
        return "end"

    # Public methods
    async def process(self, message: str, history: List[Dict[str, Any]]) -> AgentOutput:
        """Process a message through the agent graph asynchronously."""
        initial_state: AgentState = {
            "message": message,
            "history": history,
            "agents": self.agents,
            "current_agent_index": 0,
            "final_output": None,
            "agent_handled": False  # Track if any agent successfully handled the request
        }
        try:
            final_state = await self.graph.ainvoke(initial_state)
            
            # Get the final output or create a default response
            final_output = final_state.get('final_output')
            if final_output is None or (not final_output.response and not final_output.tool_used):
                final_output = AgentOutput(
                    response="Sorry, I couldn't understand your request. Could you please rephrase?",
                    tool_used=False,
                    notifications=[]
                )
            
            return final_output
            
        except Exception as e:
            logger.error(f"Error invoking agent graph: {e}", exc_info=True)
            # Return a friendly error response instead of None
            return AgentOutput(
                response="I apologize, but I encountered an error processing your request. Please try again.",
                tool_used=False,
                notifications=["Error: Internal processing failed"]
            )

    def get_all_tools(self) -> List[Dict[str, Any]]:
        all_tools = []
        for agent in self.agents:
            all_tools.extend(agent.get_available_tools())
        return all_tools

# --- End of Corrected Class Definition ---

# Example Usage (using the corrected class) - Keep prints here for direct script run test
if __name__ == '__main__':
    import asyncio

    # Configure root logger for testing if run directly
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    async def main():
        # Use the corrected manager
        manager = AgentManagerCorrected()
        print("Agent Manager Initialized (Direct Run).") # Use print for direct run feedback
        print("Agents (priority order):", [agent.name for agent in manager.agents])

        history = [{'role': 'user', 'content': 'I am in room 303.'}]
        messages = [
            "The TV remote is broken.", # Maintenance
            "I'd like to order a pizza and a coke.", # Room Service (Food)
            "What's the weather like?", # Fall through
            "Can you schedule maintenance for my AC unit for tomorrow morning?", # Maintenance
            "I'm thirsty, get me some water." # Room Service (Drink)
        ]

        for msg in messages:
            print(f"\n--- Processing Message (Direct Run): '{msg}' ---") # Use print
            result = await manager.process(msg, history)
            print(f"--- Final Result (Direct Run) for '{msg}': {result} ---") # Use print
            history.append({'role': 'user', 'content': msg})
            if result and result.response:
                history.append({'role': 'assistant', 'content': result.response})

    asyncio.run(main())