"""
Base Agent Class
All specialized agents inherit from this
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger
from core.state import AgentState


class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(
        self,
        name: str,
        role: str,
        llm: BaseChatModel,
        system_prompt: str
    ):
        """
        Initialize agent
        
        Args:
            name: Agent identifier
            role: Agent's role description
            llm: Language model instance
            system_prompt: Agent-specific instructions
        """
        self.name = name
        self.role = role
        self.llm = llm
        self.system_prompt = system_prompt
        logger.info(f"Initialized agent: {name} ({role})")
    
    @abstractmethod
    def execute(self, state: AgentState) -> AgentState:
        """
        Execute agent logic and update state
        
        Args:
            state: Current workflow state
        
        Returns:
            Updated state
        """
        pass
    
    def invoke_llm(self, user_message: str, context: str = "") -> str:
        """
        Call LLM with system and user messages
        
        Args:
            user_message: User/task message
            context: Additional context to include
        
        Returns:
            LLM response text
        """
        try:
            messages = [
                SystemMessage(content=self.system_prompt)
            ]
            
            if context:
                messages.append(SystemMessage(content=f"Context:\n{context}"))
            
            messages.append(HumanMessage(content=user_message))
            
            logger.debug(f"[{self.name}] Invoking LLM with {len(messages)} messages")
            response = self.llm.invoke(messages)
            
            return response.content
            
        except Exception as e:
            logger.error(f"[{self.name}] LLM invocation failed: {e}")
            raise
    
    def log_action(self, action: str, details: str = ""):
        """Log agent action"""
        logger.info(f"[{self.name}] {action} | {details}")
    
    def __str__(self) -> str:
        return f"Agent({self.name}, role={self.role})"