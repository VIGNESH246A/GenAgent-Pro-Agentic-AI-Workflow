"""
Memory Agent
Manages short-term and long-term memory
"""

from .base_agent import BaseAgent
from core.state import AgentState
from memory.vector_store import VectorStore
from loguru import logger


class MemoryAgent(BaseAgent):
    """Manages conversation and task memory"""
    
    def __init__(self, llm, system_prompt: str, vector_store: VectorStore):
        super().__init__(
            name="memory",
            role="Memory Manager",
            llm=llm,
            system_prompt=system_prompt
        )
        self.vector_store = vector_store
    
    def execute(self, state: AgentState) -> AgentState:
        """
        Store current context and retrieve relevant memories
        
        Args:
            state: Current workflow state
        
        Returns:
            State with retrieved context
        """
        try:
            self.log_action("Managing memory")
            
            # Store current goal and results
            self._store_current_context(state)
            
            # Retrieve relevant past context if needed
            if state["user_input"]:
                retrieved = self._retrieve_relevant_context(state["user_input"])
                state["retrieved_context"] = retrieved
            
            # Update conversation history
            state["conversation_history"].append({
                "role": "user",
                "content": state["user_input"]
            })
            
            if state.get("final_output"):
                state["conversation_history"].append({
                    "role": "assistant",
                    "content": state["final_output"]
                })
            
            self.log_action("Memory updated", f"Store size: {self.vector_store.get_stats()['total_vectors']}")
            
            # Memory agent doesn't change workflow routing
            return state
            
        except Exception as e:
            logger.error(f"[Memory] Memory operation failed: {e}")
            state["warnings"].append(f"Memory error: {str(e)}")
            return state
    
    def _store_current_context(self, state: AgentState):
        """Store current task and results in vector memory"""
        try:
            # Store user goal
            self.vector_store.add_text(
                text=f"User Goal: {state['user_goal']}",
                metadata={"type": "goal", "iteration": state["iteration_count"]}
            )
            
            # Store completed task results
            for task in state["task_plan"]:
                if task["result"]:
                    self.vector_store.add_text(
                        text=f"Task: {task['description']}\nResult: {task['result']}",
                        metadata={
                            "type": "task_result",
                            "task_id": task["id"],
                            "iteration": state["iteration_count"]
                        }
                    )
            
            # Persist to disk
            self.vector_store.save()
            
        except Exception as e:
            logger.error(f"Failed to store context: {e}")
    
    def _retrieve_relevant_context(self, query: str) -> str:
        """Retrieve relevant past context"""
        try:
            results = self.vector_store.search(query, k=3)
            
            if not results:
                return "No relevant past context found"
            
            context_parts = []
            for i, result in enumerate(results, 1):
                context_parts.append(f"[{i}] {result['text']}")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return "Memory retrieval failed"