"""
Validator Agent
Verifies task execution quality and completeness
"""

import json
from .base_agent import BaseAgent
from core.state import AgentState, TaskStatus
from loguru import logger


class ValidatorAgent(BaseAgent):
    """Validates execution outputs"""
    
    def __init__(self, llm, system_prompt: str, threshold: float = 0.8):
        super().__init__(
            name="validator",
            role="Output Validator",
            llm=llm,
            system_prompt=system_prompt
        )
        self.threshold = threshold
    
    def execute(self, state: AgentState) -> AgentState:
        """
        Validate all executed tasks
        
        Args:
            state: Current workflow state
        
        Returns:
            State with validation results
        """
        try:
            # LITE MODE: Skip validation for simple calculator tasks
            if self._is_simple_calculator_task(state):
                self.log_action("Skipping validation (simple calculator task)")
                state["validation_passed"] = True
                state["validation_result"] = {
                    "valid": True,
                    "score": 1.0,
                    "feedback": "Auto-validated: Simple calculator task completed successfully"
                }
                state["final_output"] = self._compile_final_output(state)
                state["next_agent"] = "end"
                state["is_complete"] = True
                return state
            
            self.log_action("Validating execution results")
            
            # Collect all results
            completed_tasks = [t for t in state["task_plan"] if t["status"] == TaskStatus.COMPLETED]
            failed_tasks = [t for t in state["task_plan"] if t["status"] == TaskStatus.FAILED]
            
            if not completed_tasks and not failed_tasks:
                logger.warning("No tasks to validate")
                state["validation_passed"] = False
                state["next_agent"] = "end"
                state["is_complete"] = True
                return state
            
            # Build validation prompt
            validation_prompt = self._build_validation_prompt(state, completed_tasks, failed_tasks)
            
            # Get validation from LLM
            validation_response = self.invoke_llm(validation_prompt)
            
            # Parse validation result
            validation_result = self._parse_validation(validation_response)
            
            state["validation_result"] = validation_result
            is_valid = validation_result.get("valid", False)
            score = validation_result.get("score", 0.0)
            feedback = validation_result.get("feedback", "")
            
            self.log_action(
                f"Validation {'PASSED' if is_valid else 'FAILED'}",
                f"Score: {score:.2f} | {feedback}"
            )
            
            # Decide next action
            if is_valid and score >= self.threshold:
                # Success - compile final output
                state["validation_passed"] = True
                state["final_output"] = self._compile_final_output(state)
                state["next_agent"] = "end"
                state["is_complete"] = True
            else:
                # Failed validation
                if state["retry_count"] < 2:  # Max 2 retries
                    logger.warning(f"Validation failed, retry {state['retry_count'] + 1}")
                    state["validation_passed"] = False
                    state["retry_count"] += 1
                    state["warnings"].append(f"Retry {state['retry_count']}: {feedback}")
                    
                    # Reset to re-execute failed tasks
                    state["current_task_index"] = 0
                    for task in state["task_plan"]:
                        if task["status"] == TaskStatus.FAILED:
                            task["status"] = TaskStatus.PENDING
                    
                    state["next_agent"] = "executor"
                else:
                    logger.error("Max retries exceeded")
                    state["validation_passed"] = False
                    state["errors"].append("Validation failed after max retries")
                    state["final_output"] = self._compile_final_output(state)
                    state["next_agent"] = "end"
                    state["is_complete"] = True
            
            return state
            
        except Exception as e:
            logger.error(f"[Validator] Validation failed: {e}")
            state["errors"].append(f"Validation error: {str(e)}")
            state["validation_passed"] = False
            state["next_agent"] = "end"
            state["is_complete"] = True
            return state
    
    def _build_validation_prompt(self, state: AgentState, completed_tasks, failed_tasks) -> str:
        """Build validation prompt"""
        completed_str = "\n".join([
            f"- {t['id']}: {t['description']}\n  Result: {t['result'][:200]}"
            for t in completed_tasks
        ])
        
        failed_str = "\n".join([
            f"- {t['id']}: {t['description']}\n  Error: {t['error']}"
            for t in failed_tasks
        ]) if failed_tasks else "None"
        
        prompt = f"""
Original Goal: {state['user_goal']}

Completed Tasks:
{completed_str}

Failed Tasks:
{failed_str}

Evaluate if the goal was achieved successfully.
Consider:
1. Were all required tasks completed?
2. Do results make sense and answer the goal?
3. Are there any errors or inconsistencies?
4. Is the quality acceptable?

Output ONLY valid JSON:
{{
  "valid": true/false,
  "score": 0.0-1.0,
  "feedback": "Detailed feedback on what worked or failed"
}}
"""
        return prompt
    
    def _parse_validation(self, response: str) -> dict:
        """Parse validation JSON from LLM response"""
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                return {"valid": False, "score": 0.0, "feedback": "Invalid validation format"}
            
            json_str = response[start_idx:end_idx]
            result = json.loads(json_str)
            
            return {
                "valid": result.get("valid", False),
                "score": float(result.get("score", 0.0)),
                "feedback": result.get("feedback", "")
            }
            
        except Exception as e:
            logger.error(f"Failed to parse validation: {e}")
            return {"valid": False, "score": 0.0, "feedback": f"Parse error: {str(e)}"}
    
    def _compile_final_output(self, state: AgentState) -> str:
        """Compile final output from all results"""
        output_parts = [f"Goal: {state['user_goal']}\n"]
        
        for task in state["task_plan"]:
            if task["status"] == TaskStatus.COMPLETED:
                output_parts.append(f"✓ {task['description']}")
                output_parts.append(f"  Result: {task['result']}\n")
            elif task["status"] == TaskStatus.FAILED:
                output_parts.append(f"✗ {task['description']}")
                output_parts.append(f"  Error: {task['error']}\n")
        
        if state["validation_result"]:
            output_parts.append(f"\nValidation: {state['validation_result']['feedback']}")
        
        return "\n".join(output_parts)
    
    def _is_simple_calculator_task(self, state: AgentState) -> bool:
        """
        Check if this is a simple calculator-only task that doesn't need validation
        
        Returns:
            True if all tasks use only calculator tool
        """
        try:
            # Check if all tool calls were calculator only
            for tool_call in state.get("tool_calls", []):
                result = tool_call.get("result", "")
                if "calculator" not in result.lower():
                    return False
            
            # Check if no errors occurred
            if state.get("errors"):
                return False
            
            # Check if all tasks completed
            completed = [t for t in state["task_plan"] if t["status"] == TaskStatus.COMPLETED]
            if len(completed) != len(state["task_plan"]):
                return False
            
            return True
        except:
            return False