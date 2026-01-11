"""
Integration Tests for GenAgent Pro Workflow
"""

import pytest
import os
from dotenv import load_dotenv
from core.orchestrator import WorkflowOrchestrator
from tools.calculator import CalculatorTool
from tools.python_executor import PythonExecutorTool
from memory.vector_store import VectorStore


@pytest.fixture(scope="module")
def setup_environment():
    """Setup test environment"""
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY not set")
    yield
    # Cleanup if needed


@pytest.fixture
def orchestrator(setup_environment):
    """Create orchestrator instance"""
    return WorkflowOrchestrator()


@pytest.fixture
def calculator():
    """Create calculator tool instance"""
    return CalculatorTool()


@pytest.fixture
def python_executor():
    """Create Python executor instance"""
    return PythonExecutorTool()


@pytest.fixture
def vector_store():
    """Create vector store instance"""
    return VectorStore(store_path="./data/test_memory")


class TestCalculatorTool:
    """Test calculator tool"""
    
    def test_simple_addition(self, calculator):
        result = calculator.execute("5 + 3")
        assert result["success"] is True
        assert result["result"] == "8"
    
    def test_complex_expression(self, calculator):
        result = calculator.execute("(10 + 5) * 2 / 3")
        assert result["success"] is True
        assert float(result["result"]) == 10.0
    
    def test_math_functions(self, calculator):
        result = calculator.execute("sqrt(16) + pow(2, 3)")
        assert result["success"] is True
        assert float(result["result"]) == 12.0
    
    def test_invalid_expression(self, calculator):
        result = calculator.execute("invalid expression !@#")
        assert result["success"] is False
        assert "error" in result


class TestPythonExecutor:
    """Test Python executor tool"""
    
    def test_simple_code(self, python_executor):
        code = "print('Hello, World!')"
        result = python_executor.execute(code)
        assert result["success"] is True
        assert "Hello, World!" in result["result"]
    
    def test_math_operations(self, python_executor):
        code = """
import math
result = math.sqrt(144)
print(f"Square root of 144 is {result}")
"""
        result = python_executor.execute(code)
        assert result["success"] is True
        assert "12" in result["result"]
    
    def test_fibonacci(self, python_executor):
        code = """
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

print([fib(i) for i in range(10)])
"""
        result = python_executor.execute(code)
        assert result["success"] is True
        assert "[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]" in result["result"]
    
    def test_security_block(self, python_executor):
        """Test that dangerous operations are blocked"""
        code = "import os; os.system('ls')"
        result = python_executor.execute(code)
        assert result["success"] is False
        assert "SecurityError" in result.get("error_type", "")


class TestVectorStore:
    """Test vector memory store"""
    
    def test_add_and_search(self, vector_store):
        # Add documents
        vector_store.add_text("Python is a programming language")
        vector_store.add_text("JavaScript is used for web development")
        vector_store.add_text("Machine learning uses Python")
        
        # Search
        results = vector_store.search("programming with Python", k=2)
        assert len(results) > 0
        assert any("Python" in r["text"] for r in results)
    
    def test_empty_search(self, vector_store):
        vector_store.clear()
        results = vector_store.search("test query")
        assert len(results) == 0


class TestWorkflow:
    """Test end-to-end workflow"""
    
    def test_simple_calculation(self, orchestrator):
        """Test simple calculation workflow"""
        result = orchestrator.run("Calculate the average of 10, 20, 30, 40, 50")
        
        assert result["success"] is True
        assert result["validation_passed"] is True
        assert "30" in result["output"] or "average" in result["output"].lower()
    
    def test_multi_step_task(self, orchestrator):
        """Test multi-step task execution"""
        result = orchestrator.run("Calculate 5 + 3, then multiply the result by 2")
        
        assert result["success"] is True
        assert result["iterations"] > 1  # Should have multiple steps
        assert "16" in result["output"]
    
    def test_error_handling(self, orchestrator):
        """Test that errors are handled gracefully"""
        result = orchestrator.run("Do something completely impossible and undefined")
        
        # Should not crash, even if it fails
        assert "success" in result
        assert "output" in result


@pytest.mark.slow
class TestComplexWorkflows:
    """Test complex multi-agent workflows"""
    
    def test_python_execution_workflow(self, orchestrator):
        """Test Python code generation and execution"""
        result = orchestrator.run("Write Python code to generate first 5 Fibonacci numbers")
        
        assert result["success"] is True
        # Should contain Fibonacci sequence
        assert any(num in result["output"] for num in ["0", "1", "2", "3", "5"])
    
    def test_planning_quality(self, orchestrator):
        """Test that planner creates reasonable plans"""
        result = orchestrator.run("Calculate 10% of 500 and then add 25 to it")
        
        assert result["success"] is True
        assert result["iterations"] >= 2  # Should plan multiple steps
        assert "75" in result["output"] or "seventy" in result["output"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])