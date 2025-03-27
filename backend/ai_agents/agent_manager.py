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

# Define the state for the graph
class AgentState(TypedDict):
    message: str
    history: List[Dict[str, Any]]
    agents: List[Any] # List of agent instances, sorted by priority
    current_agent_index: int
    final_output: Optional[AgentOutput] # Store the result from the handling agent

# --- Start of Corrected Class Definition ---
class AgentManagerCorrected:
    """
    Manages a collection of agents and processes messages through them using LangGraph.
    Uses refined node logic for clarity.
    """
    def __init__(self):
        self.agents = sorted(
            [RoomServiceAgent(), MaintenanceAgent()],
            key=lambda agent: agent.priority,
            reverse=True
        )
        self.graph = self._build_graph()

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

    async def _run_agent_node(self, state: AgentState) -> AgentState:
        agent_index = state['current_agent_index']
        if agent_index >= len(state['agents']):
            # Use logger instead of print
            logger.info(f"Run: Invalid index {agent_index}, skipping run")
            if state.get('final_output') is None:
                 state['final_output'] = AgentOutput(response="", tool_used=False, notifications=[])
            return state

        agent = state['agents'][agent_index]
        message = state['message']
        history = state['history']
        # Use logger instead of print
        logger.info(f"Run: Agent {agent.name}")
        if agent.should_handle(message, history):
             # Use logger instead of print
            logger.info(f"Run: Agent {agent.name} SHOULD handle")
            try:
                output: AgentOutput = await agent.process(message, history)
                # Use logger instead of print
                logger.info(f"Run: Agent {agent.name} output: {output!r}") # Log repr for detail
                if output and (getattr(output, 'response', None) or getattr(output, 'tool_used', False)):
                     state['final_output'] = output
                else:
                     # Agent handled but produced no result -> treat as not handled
                     logger.warning(f"Run: Agent {agent.name} handled but produced no actionable output.")
                     state['final_output'] = None
            except Exception as e:
                logger.error(f"Run: Error during agent {agent.name} process method: {e}", exc_info=True)
                state['final_output'] = None # Treat as not handled on error
        else:
             # Use logger instead of print
            logger.info(f"Run: Agent {agent.name} should NOT handle")
            state['final_output'] = None
        return state

    # Edge Logic
    def _decide_next_step_edge(self, state: AgentState) -> str:
        agent_output = state.get('final_output')
        current_index = state['current_agent_index']

        # Check if agent_output is valid and has response/tool_used
        if agent_output and (getattr(agent_output, 'response', None) or getattr(agent_output, 'tool_used', False)):
            # Use logger instead of print
            logger.info(f"Decide: Agent {state['agents'][current_index].name} handled. END")
            return "end"
        else:
            next_index = current_index + 1
            if next_index < len(state['agents']):
                 # Use logger instead of print
                logger.info(f"Decide: Agent {state['agents'][current_index].name} did not handle. CONTINUE to index {next_index}")
                # *** IMPORTANT: Update state for the next node ***
                state['current_agent_index'] = next_index
                state['final_output'] = None # Clear output before next agent
                return "continue"
            else:
                 # Use logger instead of print
                logger.info(f"Decide: Agent {state['agents'][current_index].name} did not handle. No more agents. END (fall-through)")
                if state.get('final_output') is None: # Ensure fall-through if not set
                     state['final_output'] = AgentOutput(response="", tool_used=False, notifications=[])
                return "end"

    # Public methods
    async def process(self, message: str, history: List[Dict[str, Any]]) -> Optional[AgentOutput]: # Return Optional
        initial_state: AgentState = {
            "message": message,
            "history": history,
            "agents": self.agents,
            "current_agent_index": 0,
            "final_output": None
        }
        try:
            final_state = await self.graph.ainvoke(initial_state)
            # Return the final output stored in the state
            # If no agent handled it, final_output should be the default fall-through (which might be None initially)
            return final_state.get('final_output') # Return None if not set
        except Exception as e:
            logger.error(f"Error invoking agent graph: {e}", exc_info=True)
            return None # Return None on graph error

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