"""
Executor Agent
Executes tasks using available tools
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from core.state import AgentState, TaskStatus
from tools.base_tool import BaseTool
from loguru import logger


class ExecutorAgent(BaseAgent):
    """Executes tasks using tools"""
    
    def __init__(self, llm, system_prompt: str, tools: List[BaseTool]):
        super().__init__(
            name="executor",
            role="Task Executor",
            llm=llm,
            system_prompt=system_prompt
        )
        self.tools = {tool.name: tool for tool in tools}
        logger.info(f"Executor initialized with {len(self.tools)} tools: {list(self.tools.keys())}")
    
    def execute(self, state: AgentState) -> AgentState:
        """
        Execute current task using appropriate tools
        
        Args:
            state: Current workflow state
        
        Returns:
            State with execution results
        """
        try:
            # Get current task
            task_index = state["current_task_index"]
            if task_index >= len(state["task_plan"]):
                self.log_action("All tasks completed")
                state["next_agent"] = "validator"
                return state
            
            current_task = state["task_plan"][task_index]
            self.log_action(f"Executing task {task_index + 1}/{len(state['task_plan'])}", 
                          current_task["description"])
            
            # Check dependencies
            if not self._check_dependencies(current_task, state):
                error_msg = f"Dependencies not met for {current_task['id']}"
                logger.error(error_msg)
                current_task["status"] = TaskStatus.FAILED
                current_task["error"] = error_msg
                state["errors"].append(error_msg)
                state["next_agent"] = "validator"
                return state
            
            # Mark as in progress
            current_task["status"] = TaskStatus.IN_PROGRESS
            
            # Build execution prompt with context
            execution_prompt = self._build_execution_prompt(current_task, state)
            
            # Get LLM decision on which tool to use
            llm_response = self.invoke_llm(execution_prompt)
            
            # Extract tool usage and execute
            result = self._execute_with_tools(llm_response, current_task)
            
            # Update task
            current_task["status"] = TaskStatus.COMPLETED
            current_task["result"] = result
            
            # Store result
            state["execution_results"][current_task["id"]] = result
            
            # Add to tool calls log
            state["tool_calls"].append({
                "task_id": current_task["id"],
                "description": current_task["description"],
                "result": result
            })
            
            self.log_action(f"Task {current_task['id']} completed", f"Result: {result[:100]}")
            
            # Move to next task
            state["current_task_index"] += 1
            state["iteration_count"] += 1
            
            # Check if more tasks remain
            if state["current_task_index"] < len(state["task_plan"]):
                state["next_agent"] = "executor"  # Continue with next task
            else:
                state["next_agent"] = "validator"  # All tasks done, validate
            
            return state
            
        except Exception as e:
            logger.error(f"[Executor] Execution failed: {e}")
            if task_index < len(state["task_plan"]):
                state["task_plan"][task_index]["status"] = TaskStatus.FAILED
                state["task_plan"][task_index]["error"] = str(e)
            state["errors"].append(f"Execution error: {str(e)}")
            state["next_agent"] = "validator"
            return state
    
    def _check_dependencies(self, task: Dict, state: AgentState) -> bool:
        """Check if task dependencies are completed"""
        for dep_id in task["dependencies"]:
            dep_task = next((t for t in state["task_plan"] if t["id"] == dep_id), None)
            if not dep_task or dep_task["status"] != TaskStatus.COMPLETED:
                return False
        return True
    
    def _build_execution_prompt(self, task: Dict, state: AgentState) -> str:
        """Build execution prompt with context"""
        # Get previous results for context
        context = []
        for dep_id in task["dependencies"]:
            if dep_id in state["execution_results"]:
                context.append(f"Result from {dep_id}: {state['execution_results'][dep_id]}")
        
        context_str = "\n".join(context) if context else "No previous results"
        
        prompt = f"""
Task: {task['description']}

Previous Results:
{context_str}

Available Tools:
{self._format_tools_description()}

Instructions:
1. Analyze the task
2. Decide which tool(s) to use
3. Provide tool name and inputs
4. Format: TOOL: <tool_name> | INPUT: <input_data>

Example: TOOL: calculator | INPUT: 5 + 3 * 2
"""
        return prompt
    
    def _format_tools_description(self) -> str:
        """Format tool descriptions for prompt"""
        descriptions = []
        for name, tool in self.tools.items():
            descriptions.append(f"- {name}: {tool.description}")
        return "\n".join(descriptions)
    
    def _execute_with_tools(self, llm_response: str, task: Dict) -> str:
        """Parse LLM response and execute appropriate tool"""
        try:
            # Parse tool call from response
            if "TOOL:" in llm_response and "INPUT:" in llm_response:
                tool_name = llm_response.split("TOOL:")[1].split("|")[0].strip()
                tool_input = llm_response.split("INPUT:")[1].strip()
                
                if tool_name in self.tools:
                    logger.info(f"Executing tool: {tool_name} with input: {tool_input[:50]}")
                    tool_result = self.tools[tool_name].execute(tool_input)
                    
                    if tool_result["success"]:
                        return f"Tool {tool_name} executed successfully:\n{tool_result['result']}"
                    else:
                        return f"Tool {tool_name} failed: {tool_result['error']}"
                else:
                    logger.warning(f"Tool {tool_name} not found, using LLM response directly")
            
            # If no tool call detected, return LLM response as-is
            return llm_response
            
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return f"Tool execution failed: {str(e)}"