"""
LangGraph Orchestrator
Defines workflow state machine and agent routing
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from core.state import AgentState, create_initial_state
from core.llm_factory import get_llm_factory
from agents.planner_agent import PlannerAgent
from agents.executor_agent import ExecutorAgent
from agents.validator_agent import ValidatorAgent
from agents.memory_agent import MemoryAgent
from tools.calculator import CalculatorTool
from tools.file_reader import FileReaderTool
from tools.python_executor import PythonExecutorTool
from tools.memory_search import MemorySearchTool
from memory.vector_store import VectorStore
from loguru import logger


class WorkflowOrchestrator:
    """
    LangGraph-based workflow orchestrator
    Manages multi-agent task execution flow
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize orchestrator with all agents and tools"""
        logger.info("Initializing Workflow Orchestrator")
        
        # Initialize LLM factory
        self.llm_factory = get_llm_factory()
        
        # Initialize memory
        self.vector_store = VectorStore()
        
        # Initialize tools
        self.tools = [
            CalculatorTool(),
            FileReaderTool(),
            PythonExecutorTool(),
            MemorySearchTool(self.vector_store)
        ]
        
        # Initialize agents
        self.planner = PlannerAgent(
            llm=self.llm_factory.create_planner_llm(),
            system_prompt=self.llm_factory.get_system_prompt("planner")
        )
        
        self.executor = ExecutorAgent(
            llm=self.llm_factory.create_executor_llm(),
            system_prompt=self.llm_factory.get_system_prompt("executor"),
            tools=self.tools
        )
        
        self.validator = ValidatorAgent(
            llm=self.llm_factory.create_validator_llm(),
            system_prompt=self.llm_factory.get_system_prompt("validator")
        )
        
        self.memory = MemoryAgent(
            llm=self.llm_factory.create_memory_llm(),
            system_prompt=self.llm_factory.get_system_prompt("memory"),
            vector_store=self.vector_store
        )
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        
        logger.info("Orchestrator initialized successfully")
    
    def _build_workflow(self) -> StateGraph:
        """
        Build LangGraph state machine
        
        Flow: START → Planner → Executor → Validator → (Memory) → END
                                    ↑          ↓
                                    └──────────┘ (retry loop)
        """
        workflow = StateGraph(AgentState)
        
        # Add agent nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("executor", self._executor_node)
        workflow.add_node("validator", self._validator_node)
        workflow.add_node("memory", self._memory_node)
        
        # Define entry point
        workflow.set_entry_point("planner")
        
        # Add conditional edges (routing logic)
        workflow.add_conditional_edges(
            "planner",
            self._route_from_planner,
            {
                "executor": "executor",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "executor",
            self._route_from_executor,
            {
                "executor": "executor",  # Continue to next task
                "validator": "validator",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "validator",
            self._route_from_validator,
            {
                "executor": "executor",  # Retry
                "memory": "memory",
                "end": END
            }
        )
        
        workflow.add_edge("memory", END)
        
        return workflow.compile()
    
    # Agent Node Functions
    def _planner_node(self, state: AgentState) -> AgentState:
        """Execute planner agent"""
        logger.info("=== PLANNER NODE ===")
        return self.planner.execute(state)
    
    def _executor_node(self, state: AgentState) -> AgentState:
        """Execute executor agent"""
        logger.info("=== EXECUTOR NODE ===")
        return self.executor.execute(state)
    
    def _validator_node(self, state: AgentState) -> AgentState:
        """Execute validator agent"""
        logger.info("=== VALIDATOR NODE ===")
        return self.validator.execute(state)
    
    def _memory_node(self, state: AgentState) -> AgentState:
        """Execute memory agent"""
        logger.info("=== MEMORY NODE ===")
        return self.memory.execute(state)
    
    # Routing Logic
    def _route_from_planner(self, state: AgentState) -> str:
        """Route after planning"""
        if state["next_agent"] == "end" or not state["task_plan"]:
            return "end"
        return "executor"
    
    def _route_from_executor(self, state: AgentState) -> str:
        """Route after execution"""
        next_agent = state.get("next_agent", "end")
        if next_agent == "executor":
            return "executor"  # More tasks to execute
        elif next_agent == "validator":
            return "validator"
        return "end"
    
    def _route_from_validator(self, state: AgentState) -> str:
        """Route after validation"""
        if state["is_complete"]:
            if state["validation_passed"]:
                return "memory"  # Store results before ending
            return "end"
        else:
            return "executor"  # Retry failed tasks
    
    def run(self, user_input: str) -> Dict[str, Any]:
        """
        Execute full workflow for user input
        
        Args:
            user_input: User's goal or request
        
        Returns:
            Final workflow state with results
        """
        logger.info(f"Starting workflow for: {user_input}")
        
        # Create initial state
        initial_state = create_initial_state(user_input)
        
        # Execute workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            
            logger.info("Workflow completed successfully")
            return {
                "success": True,
                "output": final_state.get("final_output", "No output generated"),
                "validation_passed": final_state.get("validation_passed", False),
                "iterations": final_state.get("iteration_count", 0),
                "errors": final_state.get("errors", []),
                "warnings": final_state.get("warnings", [])
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "success": False,
                "output": f"Workflow failed: {str(e)}",
                "validation_passed": False,
                "iterations": 0,
                "errors": [str(e)],
                "warnings": []
            }