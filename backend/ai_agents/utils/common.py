"""
Common utility functions for the Hotel AI Assistant.

This module provides utility functions used throughout the application.
"""

import logging
import re
import json
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID.
    
    Args:
        prefix: A prefix for the ID
        
    Returns:
        A unique ID
    """
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"


def format_datetime(dt: Union[datetime, str], format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a datetime object or string as a string.
    
    Args:
        dt: The datetime to format
        format_str: The format string
        
    Returns:
        The formatted datetime string
    """
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            try:
                dt = datetime.strptime(dt, "%Y-%m-%d")
            except ValueError:
                return dt
    
    return dt.strftime(format_str)


def anonymize_pii(text: str) -> str:
    """Anonymize personally identifiable information in text.
    
    Args:
        text: The text to anonymize
        
    Returns:
        The anonymized text
    """
    # Replace email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    # Replace phone numbers
    text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[PHONE]', text)
    
    # Replace credit card numbers
    text = re.sub(r'\b(?:\d{4}[-\s]?){3}\d{4}\b', '[CREDIT_CARD]', text)
    
    # Replace SSNs
    text = re.sub(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b', '[SSN]', text)
    
    # Replace passport numbers (simple pattern)
    text = re.sub(r'\b[A-Z]{1,2}\d{6,9}\b', '[PASSPORT]', text)
    
    return text


def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract entities from text.
    
    Args:
        text: The text to extract entities from
        
    Returns:
        A dictionary of entity types and values
    """
    entities = {
        "dates": [],
        "times": [],
        "room_numbers": [],
        "booking_ids": [],
        "amounts": []
    }
    
    # Extract dates (YYYY-MM-DD or MM/DD/YYYY)
    date_patterns = [
        r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
        r'\b\d{1,2}/\d{1,2}/\d{4}\b'  # MM/DD/YYYY
    ]
    for pattern in date_patterns:
        entities["dates"].extend(re.findall(pattern, text))
    
    # Extract times (HH:MM or HH:MM:SS)
    time_patterns = [
        r'\b\d{1,2}:\d{2}(:\d{2})?\b'  # HH:MM or HH:MM:SS
    ]
    for pattern in time_patterns:
        entities["times"].extend(re.findall(pattern, text))
    
    # Extract room numbers (e.g., 101, 2B, etc.)
    room_patterns = [
        r'\broom\s+(\d+[A-Za-z]?)\b',  # "room 101" or "room 2B"
        r'\b(\d+[A-Za-z]?)\s+room\b'   # "101 room" or "2B room"
    ]
    for pattern in room_patterns:
        entities["room_numbers"].extend(re.findall(pattern, text, re.IGNORECASE))
    
    # Extract booking IDs (e.g., BK12345)
    booking_patterns = [
        r'\b(BK\d+)\b',  # BK12345
        r'\bbooking\s+(?:id|number)?\s*[:#]?\s*(\w+)\b'  # booking id: ABC123
    ]
    for pattern in booking_patterns:
        entities["booking_ids"].extend(re.findall(pattern, text, re.IGNORECASE))
    
    # Extract monetary amounts
    amount_patterns = [
        r'\$\s*(\d+(?:\.\d{2})?)',  # $123 or $123.45
        r'(\d+(?:\.\d{2})?)\s*dollars'  # 123 dollars or 123.45 dollars
    ]
    for pattern in amount_patterns:
        entities["amounts"].extend(re.findall(pattern, text, re.IGNORECASE))
    
    return entities


def parse_json_safely(text: str) -> Optional[Dict[str, Any]]:
    """Parse JSON safely, handling errors.
    
    Args:
        text: The JSON text to parse
        
    Returns:
        The parsed JSON, or None if parsing failed
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {e}")
        
        # Try to extract JSON from text (e.g., if it's embedded in other text)
        json_pattern = r'(\{.*\})'
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        return None


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to a maximum length.
    
    Args:
        text: The text to truncate
        max_length: The maximum length
        suffix: The suffix to add if truncated
        
    Returns:
        The truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate the similarity between two texts.
    
    This is a simple implementation using character-level Jaccard similarity.
    For production use, consider using a more sophisticated approach.
    
    Args:
        text1: The first text
        text2: The second text
        
    Returns:
        A similarity score between 0 and 1
    """
    # Convert to sets of characters
    set1 = set(text1.lower())
    set2 = set(text2.lower())
    
    # Calculate Jaccard similarity
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0