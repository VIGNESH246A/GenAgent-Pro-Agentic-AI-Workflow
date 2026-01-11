"""
Memory Search Tool
Searches vector store for relevant past information
"""

from typing import Dict, Any
from .base_tool import BaseTool
from memory.vector_store import VectorStore
from loguru import logger


class MemorySearchTool(BaseTool):
    """Search vector memory for relevant context"""
    
    def __init__(self, vector_store: VectorStore):
        super().__init__(
            name="memory_search",
            description="Search past conversation memory for relevant context"
        )
        self.vector_store = vector_store
    
    def execute(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Search memory for relevant information
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
        
        Returns:
            Dict with search results
        """
        try:
            logger.info(f"[MemorySearch] Searching for: {query}")
            
            results = self.vector_store.search(query, k=max_results)
            
            if not results:
                return self._success_response(
                    result="No relevant memories found",
                    metadata={"count": 0, "query": query}
                )
            
            # Format results as readable text
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(
                    f"[{i}] (Score: {result['similarity_score']:.2f})\n{result['text']}"
                )
            
            result_text = "\n\n".join(formatted_results)
            
            logger.info(f"[MemorySearch] Found {len(results)} relevant memories")
            
            return self._success_response(
                result=result_text,
                metadata={
                    "count": len(results),
                    "query": query,
                    "results": results
                }
            )
            
        except Exception as e:
            return self._error_response(f"Memory search failed: {str(e)}", "SearchError")