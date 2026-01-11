"""
Base Tool Interface
All tools inherit from this abstract class
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from loguru import logger


class BaseTool(ABC):
    """Abstract base class for all tools"""
    
    def __init__(self, name: str, description: str):
        """
        Initialize tool
        
        Args:
            name: Tool identifier
            description: What the tool does
        """
        self.name = name
        self.description = description
        logger.debug(f"Initialized tool: {name}")
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute tool logic
        
        Returns:
            Dict with 'success', 'result', 'error' keys
        """
        pass
    
    def _success_response(self, result: Any, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Format successful execution response"""
        response = {
            "success": True,
            "result": result,
            "error": None,
            "tool": self.name
        }
        if metadata:
            response["metadata"] = metadata
        return response
    
    def _error_response(self, error: str, error_type: str = "ToolError") -> Dict[str, Any]:
        """Format error response"""
        logger.error(f"[{self.name}] {error_type}: {error}")
        return {
            "success": False,
            "result": None,
            "error": error,
            "error_type": error_type,
            "tool": self.name
        }
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
    
    def to_langchain_tool(self):
        """Convert to LangChain tool format for use with agents"""
        from langchain.tools import Tool
        
        return Tool(
            name=self.name,
            description=self.description,
            func=self.execute
        )