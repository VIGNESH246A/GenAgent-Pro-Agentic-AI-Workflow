"""
Conversation Memory
Manages short-term conversation history
"""

from typing import List, Dict, Optional
from collections import deque
from loguru import logger


class ConversationMemory:
    """Manages short-term conversation history"""
    
    def __init__(self, max_history: int = 50):
        """
        Initialize conversation memory
        
        Args:
            max_history: Maximum number of messages to retain
        """
        self.max_history = max_history
        self.messages: deque = deque(maxlen=max_history)
        logger.info(f"Conversation memory initialized (max: {max_history})")
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Add message to history
        
        Args:
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            metadata: Optional metadata
        """
        message = {
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        self.messages.append(message)
        logger.debug(f"Added {role} message to history ({len(self.messages)}/{self.max_history})")
    
    def add_user_message(self, content: str):
        """Add user message"""
        self.add_message("user", content)
    
    def add_assistant_message(self, content: str):
        """Add assistant message"""
        self.add_message("assistant", content)
    
    def add_system_message(self, content: str):
        """Add system message"""
        self.add_message("system", content)
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get conversation history
        
        Args:
            limit: Maximum number of recent messages to return
        
        Returns:
            List of messages
        """
        if limit:
            return list(self.messages)[-limit:]
        return list(self.messages)
    
    def get_context(self, num_messages: int = 10) -> str:
        """
        Get formatted context from recent messages
        
        Args:
            num_messages: Number of recent messages to include
        
        Returns:
            Formatted context string
        """
        recent = self.get_history(limit=num_messages)
        
        context_parts = []
        for msg in recent:
            role = msg["role"].capitalize()
            content = msg["content"]
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def search_history(self, keyword: str) -> List[Dict]:
        """
        Search history for messages containing keyword
        
        Args:
            keyword: Keyword to search for
        
        Returns:
            List of matching messages
        """
        keyword_lower = keyword.lower()
        return [
            msg for msg in self.messages
            if keyword_lower in msg["content"].lower()
        ]
    
    def clear(self):
        """Clear all history"""
        self.messages.clear()
        logger.info("Conversation history cleared")
    
    def get_summary(self) -> Dict:
        """
        Get summary statistics
        
        Returns:
            Dict with statistics
        """
        role_counts = {}
        for msg in self.messages:
            role = msg["role"]
            role_counts[role] = role_counts.get(role, 0) + 1
        
        return {
            "total_messages": len(self.messages),
            "role_counts": role_counts,
            "max_capacity": self.max_history,
            "usage_percent": (len(self.messages) / self.max_history) * 100
        }
    
    def __len__(self) -> int:
        """Return number of messages in history"""
        return len(self.messages)
    
    def __repr__(self) -> str:
        return f"ConversationMemory(messages={len(self.messages)}, max={self.max_history})"