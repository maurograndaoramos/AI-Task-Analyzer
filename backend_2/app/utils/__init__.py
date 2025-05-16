"""Utility functions and helpers for the AI Task Analysis System."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import json
import uuid
import re

def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}-{unique_id}" if prefix else unique_id

def sanitize_string(text: str) -> str:
    """Remove special characters and normalize whitespace."""
    # Remove special characters but keep spaces and basic punctuation
    text = re.sub(r'[^\w\s\-.,?!]', '', text)
    # Normalize whitespace
    return ' '.join(text.split())

def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)

def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO 8601 string."""
    return dt.isoformat()

def parse_datetime(dt_str: str) -> datetime:
    """Parse ISO 8601 datetime string to datetime object."""
    try:
        return datetime.fromisoformat(dt_str)
    except ValueError:
        raise ValueError(f"Invalid datetime format: {dt_str}")

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely parse JSON string with fallback to default value."""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries."""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
            
    return result

def truncate_string(text: str, max_length: int = 100, ellipsis: str = "...") -> str:
    """Truncate string to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(ellipsis)] + ellipsis

def format_error(error: Exception, include_traceback: bool = False) -> Dict[str, str]:
    """Format exception into a consistent error response."""
    error_info = {
        "error": error.__class__.__name__,
        "message": str(error),
        "timestamp": format_datetime(utc_now())
    }
    
    if include_traceback:
        import traceback
        error_info["traceback"] = traceback.format_exc()
        
    return error_info

def validate_enum_value(value: str, valid_values: list, case_sensitive: bool = False) -> str:
    """Validate that a string value is one of the valid enum values."""
    if not case_sensitive:
        value = value.lower()
        valid_values = [v.lower() for v in valid_values]
        
    if value not in valid_values:
        raise ValueError(f"Invalid value: {value}. Must be one of: {', '.join(valid_values)}")
        
    return value

def parse_list_string(list_str: str, delimiter: str = ",") -> list:
    """Parse a delimiter-separated string into a list."""
    if not list_str:
        return []
    return [item.strip() for item in list_str.split(delimiter) if item.strip()]

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

__all__ = [
    'generate_id',
    'sanitize_string',
    'utc_now',
    'format_datetime',
    'parse_datetime',
    'safe_json_loads',
    'merge_dicts',
    'truncate_string',
    'format_error',
    'validate_enum_value',
    'parse_list_string',
    'format_duration'
]
