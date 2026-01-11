"""
Calculator Tool
Safely evaluates mathematical expressions
"""

import math
import re
from typing import Dict, Any
from .base_tool import BaseTool
from loguru import logger


class CalculatorTool(BaseTool):
    """Safe mathematical expression evaluator"""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Evaluate mathematical expressions safely. Supports +, -, *, /, **, sqrt, sin, cos, tan, log, etc."
        )
        
        # Safe functions for eval
        self.safe_functions = {
            'abs': abs,
            'round': round,
            'pow': pow,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'pi': math.pi,
            'e': math.e
        }
    
    def execute(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate mathematical expression
        
        Args:
            expression: Math expression as string (e.g., "2 + 2", "sqrt(16)")
        
        Returns:
            Dict with calculation result
        """
        try:
            # Clean expression
            expression = expression.strip()
            logger.info(f"[Calculator] Evaluating: {expression}")
            
            # Security check - only allow safe characters
            if not re.match(r'^[\d\+\-\*\/\(\)\.\s\w,]+$', expression):
                return self._error_response(
                    "Invalid characters in expression. Only numbers, operators, and functions allowed.",
                    "SecurityError"
                )
            
            # Prevent dangerous operations
            dangerous_keywords = ['import', 'exec', 'eval', 'open', 'file', '__']
            if any(keyword in expression.lower() for keyword in dangerous_keywords):
                return self._error_response(
                    "Dangerous keywords detected in expression",
                    "SecurityError"
                )
            
            # Evaluate with safe namespace
            result = eval(expression, {"__builtins__": {}}, self.safe_functions)
            
            # Format result
            if isinstance(result, float):
                result = round(result, 10)
            
            logger.info(f"[Calculator] Result: {result}")
            return self._success_response(
                result=str(result),
                metadata={"expression": expression, "type": type(result).__name__}
            )
            
        except ZeroDivisionError:
            return self._error_response("Division by zero", "MathError")
        
        except ValueError as e:
            return self._error_response(f"Math value error: {str(e)}", "MathError")
        
        except SyntaxError:
            return self._error_response("Invalid mathematical syntax", "SyntaxError")
        
        except Exception as e:
            return self._error_response(f"Calculation failed: {str(e)}", "CalculationError")