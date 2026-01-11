"""
Shared State Definition for LangGraph Workflow
This state is passed between all agent nodes
"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from enum import Enum
import operator


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VALIDATION_FAILED = "validation_failed"


class Task(TypedDict):
    """Individual task structure"""
    id: str
    description: str
    agent: str  # "executor", "memory", etc.
    status: TaskStatus
    dependencies: List[str]
    result: Optional[str]
    error: Optional[str]


class AgentState(TypedDict):
    """
    Global workflow state shared across all agents.
    LangGraph passes this through each node.
    """
    # User Input
    user_input: str
    user_goal: str
    
    # Planning Phase
    task_plan: List[Task]
    current_task_index: int
    
    # Execution Phase
    current_task: Optional[Task]
    tool_calls: Annotated[List[Dict[str, Any]], operator.add]  # Append-only
    execution_results: Dict[str, Any]
    
    # Validation Phase
    validation_result: Optional[Dict[str, Any]]
    validation_passed: bool
    retry_count: int
    
    # Memory
    conversation_history: Annotated[List[Dict[str, str]], operator.add]
    retrieved_context: Optional[str]
    
    # Workflow Control
    next_agent: str  # "planner", "executor", "validator", "memory", "end"
    iteration_count: int
    is_complete: bool
    final_output: Optional[str]
    
    # Error Handling
    errors: Annotated[List[str], operator.add]
    warnings: Annotated[List[str], operator.add]


def create_initial_state(user_input: str) -> AgentState:
    """Create initial state from user input"""
    return AgentState(
        user_input=user_input,
        user_goal=user_input,
        task_plan=[],
        current_task_index=0,
        current_task=None,
        tool_calls=[],
        execution_results={},
        validation_result=None,
        validation_passed=False,
        retry_count=0,
        conversation_history=[],
        retrieved_context=None,
        next_agent="planner",
        iteration_count=0,
        is_complete=False,
        final_output=None,
        errors=[],
        warnings=[]
    )


def get_pending_tasks(state: AgentState) -> List[Task]:
    """Get all pending tasks from plan"""
    return [t for t in state["task_plan"] if t["status"] == TaskStatus.PENDING]


def get_completed_tasks(state: AgentState) -> List[Task]:
    """Get all completed tasks"""
    return [t for t in state["task_plan"] if t["status"] == TaskStatus.COMPLETED]


def update_task_status(state: AgentState, task_id: str, status: TaskStatus, 
                       result: Optional[str] = None, error: Optional[str] = None):
    """Update task status in the plan"""
    for task in state["task_plan"]:
        if task["id"] == task_id:
            task["status"] = status
            if result:
                task["result"] = result
            if error:
                task["error"] = error
            break