"""
Tests Package
Integration and unit tests
"""

# Test configuration
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test constants
TEST_DATA_DIR = project_root / "data" / "test_data"
TEST_MEMORY_DIR = project_root / "data" / "test_memory"

# Ensure test directories exist
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
TEST_MEMORY_DIR.mkdir(parents=True, exist_ok=True)