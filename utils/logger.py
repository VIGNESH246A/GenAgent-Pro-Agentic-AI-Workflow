"""
Centralized Logging Configuration
Uses loguru for structured logging
"""

import os
import sys
from loguru import logger
from pathlib import Path


def setup_logger(log_level: str = "INFO", log_file: str = "./data/logs/genagent.log"):
    """
    Configure loguru logger with file and console output
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file
    """
    # Remove default handler
    logger.remove()
    
    # Create logs directory
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Console handler (colorized)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # File handler (JSON format for easy parsing)
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=log_level,
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )
    
    logger.info(f"Logger initialized - Level: {log_level}, File: {log_file}")
    return logger


def log_agent_action(agent_name: str, action: str, details: str = ""):
    """Log agent-specific actions"""
    logger.info(f"[{agent_name}] {action} | {details}")


def log_tool_usage(tool_name: str, input_data: str, output_data: str = ""):
    """Log tool execution"""
    logger.debug(f"[TOOL:{tool_name}] Input: {input_data[:100]}... | Output: {output_data[:100]}...")


def log_state_transition(from_agent: str, to_agent: str, reason: str = ""):
    """Log workflow state transitions"""
    logger.info(f"[WORKFLOW] {from_agent} → {to_agent} | {reason}")


def log_error(error_type: str, error_message: str, context: dict = None):
    """Log errors with context"""
    logger.error(f"[ERROR:{error_type}] {error_message} | Context: {context}")


# Initialize logger on import
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logger(log_level)