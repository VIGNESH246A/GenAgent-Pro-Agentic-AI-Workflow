"""
Utils Package
Utility functions and helpers
"""

from .logger import setup_logger, log_agent_action, log_tool_usage, log_state_transition, log_error
from .helpers import (
    extract_json_from_text,
    clean_text,
    format_timestamp,
    validate_file_path,
    truncate_text,
    parse_list_from_text,
    safe_dict_get,
    merge_dicts,
    calculate_similarity,
    format_error_message,
    ensure_directory,
    count_tokens_estimate,
    format_duration
)

__all__ = [
    # Logger functions
    'setup_logger',
    'log_agent_action',
    'log_tool_usage',
    'log_state_transition',
    'log_error',
    
    # Helper functions
    'extract_json_from_text',
    'clean_text',
    'format_timestamp',
    'validate_file_path',
    'truncate_text',
    'parse_list_from_text',
    'safe_dict_get',
    'merge_dicts',
    'calculate_similarity',
    'format_error_message',
    'ensure_directory',
    'count_tokens_estimate',
    'format_duration'
]