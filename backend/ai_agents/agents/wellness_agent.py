"""
Wellness Agent for the Hotel AI Assistant.

This agent provides wellness services like guided meditation,
breathing exercises, and relaxation techniques.
"""

import logging
import os
from typing import Dict, List, Any, Optional, Type
from datetime import datetime
import uuid
import random

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from langchain_huggingface import HuggingFacePipeline

from ..schemas import AgentInput, AgentOutput, WellnessInput, WellnessOutput
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class WellnessAgent(BaseAgent):
    """Agent for providing wellness services."""
    
    def __init__(self, model_name: str = "gpt-4o"):
        """Initialize the Wellness Agent.
        
        Args:
            model_name: The name of the language model to use
        """
        super().__init__(
            name="wellness_agent"
        )
        
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
        logger.info("✅ Using local quantized model")
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a hotel wellness assistant. Your job is to help guests with wellness services
            like guided meditation, breathing exercises, and relaxation techniques.
            
            Follow these guidelines:
            1. Be calm, soothing, and supportive in your tone
            2. Tailor the wellness content to the guest's preferences and needs
            3. Provide clear, easy-to-follow instructions
            4. Suggest follow-up wellness activities when appropriate
            
            For meditation sessions:
            - Start with a brief introduction to set the mood
            - Guide the guest through the meditation with clear, gentle instructions
            - End with a gentle conclusion
            
            For breathing exercises:
            - Explain the benefits of the specific breathing technique
            - Provide a step-by-step guide to the breathing pattern
            - Suggest a duration appropriate for beginners (2-3 minutes)
            
            Remember that you're creating a text-based wellness experience, so make your
            descriptions vivid and your instructions clear.
            """),
            ("human", "{input}")
        ])
        
        # Available wellness sessions
        self.available_sessions = {
            "meditation": [
                "Mindfulness Meditation",
                "Body Scan Meditation",
                "Loving-Kindness Meditation",
                "Sleep Meditation",
                "Stress Relief Meditation"
            ],
            "breathing": [
                "4-7-8 Breathing",
                "Box Breathing",
                "Diaphragmatic Breathing",
                "Alternate Nostril Breathing",
                "Equal Breathing"
            ],
            "relaxation": [
                "Progressive Muscle Relaxation",
                "Guided Imagery",
                "Body Scan Relaxation",
                "Autogenic Training",
                "Yoga Nidra"
            ]
        }
    
    def load_model(self):
        """Load the local model from the correct snapshot directory"""
        # Get the root directory of the project (three levels up from the current script)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        model_path = os.path.join(project_root, "finetunedmodel-merged")
        
        logger.info(f"Loading model from: {model_path}")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True,
            local_files_only=True  # Explicitly use local files only
        )
        
        # Configure 8-bit quantization (force GPU only)
        quantization_config = BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_enable_fp32_cpu_offload=False  # Disable CPU offload
        )
        
        # Load model with 8-bit quantization on GPU only
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            trust_remote_code=True,
            local_files_only=True,  # Explicitly use local files only
            device_map="cuda:0",  # Force GPU only
            quantization_config=quantization_config,  # Use 8-bit quantization
            low_cpu_mem_usage=True  # Optimize for low CPU memory usage
        )
        
        logger.info("✅ Model loaded successfully!")
        return model, tokenizer
    
    @property
    def input_schema(self) -> Type[AgentInput]:
        """Get the input schema for this agent."""
        return WellnessInput
    
    @property
    def output_schema(self) -> Type[AgentOutput]:
        """Get the output schema for this agent."""
        return WellnessOutput
    
    async def process(self, input_data: WellnessInput) -> WellnessOutput:
        """Process a wellness service request.
        
        Args:
            input_data: The wellness service request data
            
        Returns:
            The result of the wellness service request
        """
        logger.info(f"Processing wellness request for session type: {input_data.session_type}")
        
        # Extract the latest user message
        latest_message = input_data.messages[-1].content if input_data.messages else ""
        
        # Determine session type from input or message content
        session_type = input_data.session_type
        if not session_type:
            # Try to infer session type from the message
            message_lower = latest_message.lower()
            if "meditation" in message_lower or "meditate" in message_lower:
                session_type = "meditation"
            elif "breath" in message_lower or "breathing" in message_lower:
                session_type = "breathing"
            elif "relax" in message_lower or "relaxation" in message_lower:
                session_type = "relaxation"
            else:
                # Default to meditation if we can't determine
                session_type = "meditation"
        
        # Determine duration
        duration = input_data.duration or 3  # Default to 3 minutes
        
        # Select a specific session based on the type
        if session_type in self.available_sessions:
            specific_session = random.choice(self.available_sessions[session_type])
        else:
            specific_session = "Mindfulness Meditation"  # Default
        
        # Prepare context for the LLM
        preferences = input_data.preferences or {}
        context = {
            "session_type": session_type,
            "specific_session": specific_session,
            "duration": duration,
            "preferences": ", ".join([f"{k}: {v}" for k, v in preferences.items()]) if preferences else "None specified",
            "conversation_history": "\n".join([f"{m.sender}: {m.content}" for m in input_data.messages[:-1]]),
            "latest_message": latest_message
        }
        
        # Format the input for the LLM
        formatted_input = f"""
        Session Type: {context['session_type']}
        Specific Session: {context['specific_session']}
        Duration: {context['duration']} minutes
        Preferences: {context['preferences']}
        
        Conversation History:
        {context['conversation_history']}
        
        Latest Message:
        {context['latest_message']}
        
        Please provide a {duration}-minute {specific_session} session. The user wants help with {session_type}.
        """
        
        # Format the prompt first
        formatted_prompt = self.prompt.format(input=formatted_input)
        
        # Then invoke the LLM with the formatted prompt
        llm_response = await self.llm.ainvoke(formatted_prompt)
        
        # Generate a session ID
        session_id = f"WS-{uuid.uuid4().hex[:8].upper()}"
        
        # Handle the response which might be a string or an object with a content attribute
        if hasattr(llm_response, 'content'):
            response_content = llm_response.content
        else:
            response_content = llm_response
        
        # Create the response message
        response_message = self.create_message(
            content=response_content,
            recipient="user"
        )
        
        # Generate follow-up recommendations
        follow_up_recommendations = await self._generate_follow_up_recommendations(session_type, specific_session)
        
        # Define actions
        actions = [{
            "type": "log_wellness_session",
            "session_id": session_id,
            "session_type": session_type,
            "specific_session": specific_session,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }]
        logger.info(f"WellnessAgent generated actions: {actions}") # Added for debugging
        
        # Create and return the output
        return WellnessOutput(
            messages=[response_message],
            actions=actions,
            status="completed",
            session_id=session_id,
            session_content=llm_response.content,
            follow_up_recommendations=follow_up_recommendations
        )
    
    async def _generate_follow_up_recommendations(self, session_type: str, specific_session: str) -> List[str]:
        """Generate follow-up recommendations based on the session.
        
        Args:
            session_type: The type of session
            specific_session: The specific session
            
        Returns:
            A list of follow-up recommendations
        """
        # Select different sessions of the same type
        recommendations = []
        
        if session_type in self.available_sessions:
            # Add 2 different sessions of the same type
            for _ in range(2):
                other_session = random.choice(self.available_sessions[session_type])
                if other_session != specific_session and other_session not in recommendations:
                    recommendations.append(f"Try a {other_session} session next time")
            
            # Add 1 session of a different type
            other_types = [t for t in self.available_sessions.keys() if t != session_type]
            if other_types:
                other_type = random.choice(other_types)
                other_session = random.choice(self.available_sessions[other_type])
                recommendations.append(f"For variety, consider a {other_session} session")
        
        # Add a general wellness tip
        wellness_tips = [
            "Remember to stay hydrated throughout the day",
            "Take short breaks every hour to stretch and move around",
            "Consider a short walk outside to connect with nature",
            "Practice mindfulness while eating your next meal",
            "Try to get 7-8 hours of quality sleep tonight"
        ]
        recommendations.append(random.choice(wellness_tips))
        
        return recommendations