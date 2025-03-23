"""
Supervisor Agent for the Hotel AI Assistant multi-agent system.

This module implements the supervisor agent that coordinates all specialized agents
using LangGraph for workflow management.
"""

import logging
from typing import Dict, List, Any, Optional, Callable, TypedDict, cast
import json
import os

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Import local model support
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from langchain_huggingface import HuggingFacePipeline
from langchain_core.language_models import BaseChatModel

from .agents import BaseAgent, CheckInAgent, RoomServiceAgent, WellnessAgent
from .schemas import AgentMessage, ConversationState

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """Supervisor agent that coordinates specialized agents."""
    
    def __init__(self, model_name: str = "gpt-4o"):
        """Initialize the Supervisor Agent.
        
        Args:
            model_name: The name of the language model to use
        """
        self.name = "supervisor"
        self.model_name = model_name
        
        # Always use the local quantized model
        model, tokenizer = self.load_model()
        
        # Create a text generation pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=2000,
            temperature=0.7,
            top_p=0.9,
            top_k=50,
            repetition_penalty=1.2
        )
        
        # Create a LangChain wrapper around the pipeline
        self.llm = HuggingFacePipeline(pipeline=pipe)
        print("✅ Using local quantized model")
    def load_model(self):
        """Load the local model from the correct snapshot directory"""
        # Get the root directory of the project (two levels up from the current script)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        model_path = os.path.join(project_root, "finetunedmodel-merged")
        
        print(f"Loading model from: {model_path}")
        print(f"Loading model from: {model_path}")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True,
            local_files_only=True  # Explicitly use local files only
        )
        
        # Configure 8-bit quantization
        quantization_config = BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_enable_fp32_cpu_offload=True
        )
        
        # Load model with quantization and CUDA support
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            trust_remote_code=True,
            local_files_only=True,  # Explicitly use local files only
            quantization_config=quantization_config,  # Use BitsAndBytesConfig instead of load_in_8bit
            device_map="auto"       # Automatically use CUDA if available
        )
        
        print("✅ Model loaded successfully!")
        return model, tokenizer
        
        # Create the prompt template for the supervisor
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a hotel AI supervisor that coordinates multiple specialized agents to assist hotel guests.
            Your job is to analyze the user's request and determine which specialized agent should handle it.
            
            You have access to the following agents:
            
            1. check_in_agent: Handles guest check-ins, verifies ID and payment, and updates booking records
            2. room_service_agent: Handles room service requests for towels, pillows, and other amenities
            3. wellness_agent: Provides wellness services like guided meditation and breathing exercises
            
            Based on the user's message, select the most appropriate agent to handle the request.
            If the request doesn't clearly match any agent, ask clarifying questions to determine the user's needs.
            
            Your response should be a JSON object with the following format:
            {
                "agent": "agent_name",
                "reason": "Brief explanation of why you selected this agent"
            }
            
            If you need to ask a clarifying question, respond with:
            {
                "agent": "clarify",
                "question": "Your clarifying question here"
            }
            """),
            ("human", "{input}")
        ])
    
    def _create_agent_map(self) -> Dict[str, BaseAgent]:
        """Create a map of agent names to agent instances.
        
        Returns:
            A dictionary mapping agent names to agent instances
        """
        return {
            "check_in_agent": CheckInAgent(model_name=self.model_name),
            "room_service_agent": RoomServiceAgent(model_name=self.model_name),
            "wellness_agent": WellnessAgent(model_name=self.model_name)
        }
    
    async def route_message(self, state: ConversationState) -> str:
        """Route a message to the appropriate agent.
        
        Args:
            state: The current conversation state
            
        Returns:
            The name of the agent to route to, or "supervisor" to continue with the supervisor
        """
        # If an agent is already assigned, continue with that agent
        if state["current_agent"]:
            return state["current_agent"]
        
        # Get the latest message
        if not state["messages"]:
            return "supervisor"
        
        latest_message = state["messages"][-1]
        
        # Format the input for the LLM
        formatted_input = f"""
        User message: {latest_message['content']}
        
        Previous conversation:
        {json.dumps(state['messages'][:-1], indent=2) if len(state['messages']) > 1 else 'No previous messages'}
        """
        
        # Format the prompt first
        formatted_prompt = self.prompt.format(input=formatted_input)
        
        # Then invoke the LLM with the formatted prompt
        llm_response = await self.llm.ainvoke(formatted_prompt)
        
        # Parse the response to get the agent name
        try:
            # Handle the response which might be a string or an object with a content attribute
            if hasattr(llm_response, 'content'):
                response_content = llm_response.content
            else:
                response_content = llm_response
                
            response_json = json.loads(response_content)
            
            if "agent" in response_json:
                agent_name = response_json["agent"]
                
                if agent_name == "clarify":
                    # Need to ask a clarifying question
                    clarifying_question = response_json.get("question", "Could you please provide more details about your request?")
                    
                    # Add the clarifying question to the messages
                    state["messages"].append({
                        "role": "assistant",
                        "content": clarifying_question
                    })
                    
                    # Stay with the supervisor
                    return "supervisor"
                
                # Check if the agent exists
                agent_map = self._create_agent_map()
                if agent_name in agent_map:
                    logger.info(f"Routing to agent: {agent_name}")
                    return agent_name
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing supervisor response: {e}")
        
        # Default to staying with the supervisor
        return "supervisor"
    
    async def process_supervisor(self, state: ConversationState) -> ConversationState:
        """Process a message with the supervisor.
        
        Args:
            state: The current conversation state
            
        Returns:
            The updated conversation state
        """
        # If there are no messages, return the state as is
        if not state["messages"]:
            return state
        
        # Get the latest message
        latest_message = state["messages"][-1]
        
        # If the latest message is from the assistant, return the state as is
        if latest_message["role"] == "assistant":
            return state
        
        # Route the message to an agent
        agent_name = await self.route_message(state)
        
        # Update the current agent
        state["current_agent"] = agent_name
        
        return state
    
    async def process_agent(self, state: ConversationState, agent_name: str) -> ConversationState:
        """Process a message with a specialized agent.
        
        Args:
            state: The current conversation state
            agent_name: The name of the agent to use
            
        Returns:
            The updated conversation state
        """
        # Get the agent
        agent_map = self._create_agent_map()
        if agent_name not in agent_map:
            logger.error(f"Agent not found: {agent_name}")
            return state
        
        agent = agent_map[agent_name]
        
        # Convert the messages to the agent's input format
        agent_messages = []
        for msg in state["messages"]:
            sender = "user" if msg["role"] == "user" else "system"
            recipient = "system" if msg["role"] == "user" else "user"
            
            agent_message = AgentMessage(
                id=f"msg_{len(agent_messages)}",
                timestamp=None,  # We don't have timestamps in the state
                sender=sender,
                recipient=recipient,
                content=msg["content"],
                metadata={}
            )
            agent_messages.append(agent_message)
        
        # Create the input for the agent
        input_class = agent.input_schema
        agent_input = input_class(messages=agent_messages)
        
        # Process the input with the agent
        agent_output = await agent.process(agent_input)
        
        # Add the agent's response to the messages
        for msg in agent_output.messages:
            state["messages"].append({
                "role": "assistant",
                "content": msg.content
            })
        
        # Store the agent's output
        state["agent_outputs"][agent_name] = {
            "actions": agent_output.actions,
            "status": agent_output.status,
            "metadata": agent_output.metadata
        }
        
        # Reset the current agent if the agent has completed its task
        if agent_output.status in ["completed", "error"]:
            state["current_agent"] = None
        
        return state
    
    def create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for the supervisor and agents.
        
        Returns:
            The LangGraph workflow
        """
        # Create the workflow
        workflow = StateGraph(ConversationState)
        
        # Add the supervisor node
        workflow.add_node("supervisor", self.process_supervisor)
        
        # Add nodes for each agent
        agent_map = self._create_agent_map()
        for agent_name, agent in agent_map.items():
            workflow.add_node(
                agent_name,
                lambda state, agent_name=agent_name: self.process_agent(state, agent_name)
            )
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "supervisor",
            self.route_message
        )
        
        # Add edges from each agent back to the supervisor
        for agent_name in agent_map:
            workflow.add_edge(agent_name, "supervisor")
        
        # Set the entry point
        workflow.set_entry_point("supervisor")
        
        return workflow


def create_hotel_supervisor(model_name: str = "gpt-4o") -> StateGraph:
    """Create a hotel supervisor workflow.
    
    Args:
        model_name: The name of the language model to use
        
    Returns:
        The LangGraph workflow for the hotel supervisor
    """
    supervisor = SupervisorAgent(model_name=model_name)
    return supervisor.create_workflow()