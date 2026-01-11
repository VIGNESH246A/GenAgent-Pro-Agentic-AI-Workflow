"""
Utility Helper Functions
Common utilities used across the application
"""

import json
import re
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path


def extract_json_from_text(text: str) -> Optional[Dict]:
    """
    Extract JSON object from text that may contain other content
    
    Args:
        text: Text potentially containing JSON
    
    Returns:
        Parsed JSON dict or None
    """
    try:
        # Try direct parse first
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    try:
        # Find JSON-like structure
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_str = text[start_idx:end_idx]
            return json.loads(json_str)
    except:
        pass
    
    return None


def clean_text(text: str, max_length: Optional[int] = None) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Input text
        max_length: Maximum length (truncate if longer)
    
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format datetime to readable string
    
    Args:
        dt: Datetime object (defaults to now)
    
    Returns:
        Formatted timestamp
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def validate_file_path(file_path: str, allowed_extensions: Optional[List[str]] = None) -> bool:
    """
    Validate file path existence and extension
    
    Args:
        file_path: Path to validate
        allowed_extensions: List of allowed extensions (e.g., ['.pdf', '.txt'])
    
    Returns:
        True if valid, False otherwise
    """
    path = Path(file_path)
    
    # Check existence
    if not path.exists():
        return False
    
    # Check if it's a file
    if not path.is_file():
        return False
    
    # Check extension
    if allowed_extensions:
        if path.suffix.lower() not in allowed_extensions:
            return False
    
    return True


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def parse_list_from_text(text: str) -> List[str]:
    """
    Parse a list from various text formats
    
    Args:
        text: Text containing list (comma-separated, newline-separated, etc.)
    
    Returns:
        List of items
    """
    # Try JSON parse first
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except:
        pass
    
    # Try comma-separated
    if ',' in text:
        return [item.strip() for item in text.split(',') if item.strip()]
    
    # Try newline-separated
    if '\n' in text:
        return [line.strip() for line in text.split('\n') if line.strip()]
    
    # Return as single item
    return [text.strip()] if text.strip() else []


def safe_dict_get(dictionary: Dict, key: str, default: Any = None) -> Any:
    """
    Safely get value from nested dictionary
    
    Args:
        dictionary: Dict to search
        key: Key (supports dot notation like 'parent.child')
        default: Default value if not found
    
    Returns:
        Value or default
    """
    keys = key.split('.')
    value = dictionary
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    
    return value


def merge_dicts(*dicts: Dict) -> Dict:
    """
    Merge multiple dictionaries (later dicts override earlier ones)
    
    Args:
        *dicts: Dictionaries to merge
    
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple text similarity (Jaccard similarity)
    
    Args:
        text1: First text
        text2: Second text
    
    Returns:
        Similarity score (0.0 to 1.0)
    """
    # Tokenize
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    # Jaccard similarity
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0


def format_error_message(error: Exception, context: Optional[str] = None) -> str:
    """
    Format error message for display
    
    Args:
        error: Exception object
        context: Additional context
    
    Returns:
        Formatted error message
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    if context:
        return f"[{error_type}] {error_msg} | Context: {context}"
    
    return f"[{error_type}] {error_msg}"


def ensure_directory(path: str) -> Path:
    """
    Ensure directory exists, create if not
    
    Args:
        path: Directory path
    
    Returns:
        Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def count_tokens_estimate(text: str) -> int:
    """
    Rough estimate of token count (1 token ≈ 4 characters)
    
    Args:
        text: Input text
    
    Returns:
        Estimated token count
    """
    return len(text) // 4


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string (e.g., "2m 30s")
    """
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"