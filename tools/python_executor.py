"""
Python Executor Tool
Safely execute Python code in restricted environment
"""

import sys
from io import StringIO
from typing import Dict, Any
from RestrictedPython import compile_restricted, safe_globals
from .base_tool import BaseTool
from loguru import logger


class PythonExecutorTool(BaseTool):
    """Execute Python code safely with restrictions"""
    
    def __init__(self, timeout: int = 30):
        super().__init__(
            name="python_executor",
            description="Execute Python code safely. Supports math, statistics, datetime, json, re modules."
        )
        self.timeout = timeout
        
        # Safe modules allowed for import
        self.allowed_modules = {
            'math': __import__('math'),
            'statistics': __import__('statistics'),
            'datetime': __import__('datetime'),
            'json': __import__('json'),
            're': __import__('re')
        }
    
    def execute(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code safely
        
        Args:
            code: Python code string to execute
        
        Returns:
            Dict with execution output and errors
        """
        try:
            logger.info(f"[PythonExecutor] Executing code ({len(code)} chars)")
            
            # Security check
            dangerous_keywords = [
                'import os', 'import sys', '__import__', 'eval',
                'compile', 'open', 'file', 'input', 'raw_input'
            ]
            code_lower = code.lower()
            for keyword in dangerous_keywords:
                if keyword in code_lower:
                    return self._error_response(
                        f"Dangerous operation not allowed: {keyword}",
                        "SecurityError"
                    )
            
            # Compile restricted code - FIXED
            compile_result = compile_restricted(
                code,
                filename='<inline code>',
                mode='exec'
            )
            
            # Check for compilation errors - FIXED
            if compile_result.errors:
                return self._error_response(
                    f"Compilation errors: {'; '.join(compile_result.errors)}",
                    "CompilationError"
                )
            
            # Get the actual bytecode - FIXED
            byte_code = compile_result.code
            
            # Prepare safe execution environment
            safe_locals = {}
            safe_env = safe_globals.copy()
            safe_env.update(self.allowed_modules)
            
            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            try:
                # Execute code - FIXED
                exec(byte_code, safe_env, safe_locals)
                
                # Get output
                output = captured_output.getvalue()
                
                # Get variables created
                created_vars = {
                    k: str(v) for k, v in safe_locals.items()
                    if not k.startswith('_')
                }
                
                result_text = output if output else "Code executed successfully (no output)"
                
                logger.info(f"[PythonExecutor] Success - Output: {result_text[:100]}")
                
                return self._success_response(
                    result=result_text,
                    metadata={
                        "variables": created_vars,
                        "output_length": len(output),
                        "code_length": len(code)
                    }
                )
                
            finally:
                sys.stdout = old_stdout
            
        except Exception as e:
            logger.error(f"[PythonExecutor] Execution failed: {str(e)}")
            return self._error_response(
                f"Execution error: {str(e)}",
                "RuntimeError"
            )
        
        except TimeoutError:
            return self._error_response(
                f"Code execution timed out after {self.timeout}s",
                "TimeoutError"
            )
