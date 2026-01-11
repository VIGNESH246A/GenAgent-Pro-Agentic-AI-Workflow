"""
Planner Agent
Decomposes user goals into executable task plans
"""

import json
from typing import List
from .base_agent import BaseAgent
from core.state import AgentState, Task, TaskStatus
from loguru import logger


class PlannerAgent(BaseAgent):
    """Strategic planner that breaks goals into tasks"""
    
    def __init__(self, llm, system_prompt: str):
        super().__init__(
            name="planner",
            role="Strategic Task Planner",
            llm=llm,
            system_prompt=system_prompt
        )
    
    def execute(self, state: AgentState) -> AgentState:
        """
        Create execution plan from user goal
        
        Args:
            state: Current workflow state
        
        Returns:
            State with populated task_plan
        """
        try:
            self.log_action("Planning tasks", f"Goal: {state['user_goal']}")
            
            # Build planning prompt
            planning_prompt = f"""
User Goal: {state['user_goal']}

Available Tools:
- file_reader: Read PDF, TXT, CSV, DOCX files
- python_executor: Execute Python code
- calculator: Perform mathematical calculations
- memory_search: Search past conversation memory

Create a step-by-step plan to achieve this goal.
Output ONLY valid JSON with this exact structure:
{{
  "tasks": [
    {{
      "id": "task_1",
      "description": "Clear description of what to do",
      "agent": "executor",
      "dependencies": []
    }},
    {{
      "id": "task_2",
      "description": "Next task description",
      "agent": "executor",
      "dependencies": ["task_1"]
    }}
  ]
}}

Rules:
1. Break complex goals into 2-8 simple tasks
2. Each task should use ONE tool or action
3. Dependencies: List task IDs that must complete first
4. Keep tasks atomic and executable
5. Always assign agent="executor" for now
"""
            
            # Get plan from LLM
            response = self.invoke_llm(planning_prompt)
            
            # Parse JSON response
            plan_data = self._parse_plan(response)
            
            # Convert to Task objects
            tasks = []
            for task_dict in plan_data.get("tasks", []):
                task = Task(
                    id=task_dict["id"],
                    description=task_dict["description"],
                    agent=task_dict.get("agent", "executor"),
                    status=TaskStatus.PENDING,
                    dependencies=task_dict.get("dependencies", []),
                    result=None,
                    error=None
                )
                tasks.append(task)
            
            self.log_action("Plan created", f"{len(tasks)} tasks generated")
            
            # Update state
            state["task_plan"] = tasks
            state["current_task_index"] = 0
            state["next_agent"] = "executor"
            state["iteration_count"] += 1
            
            # Log plan
            for i, task in enumerate(tasks, 1):
                logger.info(f"  [{i}] {task['id']}: {task['description']}")
            
            return state
            
        except Exception as e:
            logger.error(f"[Planner] Planning failed: {e}")
            state["errors"].append(f"Planning error: {str(e)}")
            state["next_agent"] = "end"
            state["is_complete"] = True
            return state
    
    def _parse_plan(self, response: str) -> dict:
        """Extract and parse JSON from LLM response"""
        try:
            # Try to find JSON in response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[start_idx:end_idx]
            plan = json.loads(json_str)
            
            if "tasks" not in plan or not isinstance(plan["tasks"], list):
                raise ValueError("Invalid plan format: missing 'tasks' array")
            
            return plan
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse plan JSON: {e}")
            logger.debug(f"Response was: {response}")
            raise ValueError(f"Invalid JSON in plan: {str(e)}")
        
        except Exception as e:
            logger.error(f"Plan parsing error: {e}")
            raise