"""
LLM Factory for Gemini Integration
Handles model initialization, retry logic, and error handling
"""

import os
from typing import Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel
from loguru import logger
import yaml


class LLMFactory:
    """Factory for creating and managing LLM instances"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize LLM factory with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.model_name = os.getenv("GEMINI_MODEL", self.config['llm']['model'])
        self.default_params = {
            'temperature': self.config['llm']['temperature'],
            'max_output_tokens': self.config['llm']['max_tokens'],
            'top_p': self.config['llm']['top_p'],
            'top_k': self.config['llm']['top_k']
        }
        
        logger.info(f"LLM Factory initialized with model: {self.model_name}")
    
    def create_llm(self, agent_type: str = "default", **kwargs) -> BaseChatModel:
        """
        Create LLM instance for specific agent
        
        Args:
            agent_type: "planner", "executor", "validator", "memory"
            **kwargs: Override default parameters
        """
        # Get agent-specific config
        agent_config = self.config['agents'].get(agent_type, {})
        
        # Merge parameters (priority: kwargs > agent_config > default)
        params = self.default_params.copy()
        if 'temperature' in agent_config:
            params['temperature'] = agent_config['temperature']
        params.update(kwargs)
        
        llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            **params
        )
        
        logger.debug(f"Created LLM for {agent_type} with params: {params}")
        return llm
    
    def create_planner_llm(self) -> BaseChatModel:
        """Create LLM optimized for planning (low temperature)"""
        return self.create_llm("planner")
    
    def create_executor_llm(self) -> BaseChatModel:
        """Create LLM optimized for execution"""
        return self.create_llm("executor")
    
    def create_validator_llm(self) -> BaseChatModel:
        """Create LLM optimized for validation (very low temperature)"""
        return self.create_llm("validator")
    
    def create_memory_llm(self) -> BaseChatModel:
        """Create LLM for memory operations"""
        return self.create_llm("memory")
    
    def get_system_prompt(self, agent_type: str) -> str:
        """Get agent-specific system prompt from config"""
        agent_config = self.config['agents'].get(agent_type, {})
        return agent_config.get('system_prompt', '')


# Global instance
_llm_factory: Optional[LLMFactory] = None


def get_llm_factory() -> LLMFactory:
    """Get or create global LLM factory instance"""
    global _llm_factory
    if _llm_factory is None:
        _llm_factory = LLMFactory()
    return _llm_factory


def create_agent_llm(agent_type: str) -> BaseChatModel:
    """Convenience function to create agent-specific LLM"""
    factory = get_llm_factory()
    return factory.create_llm(agent_type)