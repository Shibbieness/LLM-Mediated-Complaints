"""
Utility functions for the Complaint System
Handles ID generation, validation, formatting, and helper functions
"""

import re
import json
import random
import string
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

import config


def generate_complaint_id() -> str:
    """
    Generate a unique complaint ID following the pattern:
    CMP-YYYY-MM-DD-XXXXXX
    
    Returns:
        str: Unique complaint identifier
    """
    now = datetime.now()
    date_part = now.strftime("%Y-%m-%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"CMP-{date_part}-{random_part}"


def validate_complaint_schema(complaint_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate complaint data against required fields
    
    Args:
        complaint_data: Dictionary containing complaint information
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Check required fields
        required_fields = [
            "complaint_id",
            "reported_at",
            "status",
            "primary_category",
            "severity",
            "user_intent",
            "observed_outcome",
            "expected_outcome",
            "confidence"
        ]
        
        for field in required_fields:
            if field not in complaint_data:
                return False, f"Missing required field: {field}"
        
        # Validate complaint_id format
        if not re.match(r'^CMP-\d{4}-\d{2}-\d{2}-[A-Z0-9]{6}$', complaint_data["complaint_id"]):
            return False, "Invalid complaint_id format"
        
        # Validate status enum
        valid_statuses = ["new", "triaged", "structured", "clustered", "routed", 
                          "in_progress", "awaiting_user", "resolved", "closed", "reopened"]
        if complaint_data["status"] not in valid_statuses:
            return False, f"Invalid status: {complaint_data['status']}"
        
        # Validate category enum
        valid_categories = ["bug", "model_behavior", "ux_ui", "feature_request",
                            "policy_friction", "performance", "trust_safety", 
                            "misunderstanding", "other"]
        if complaint_data["primary_category"] not in valid_categories:
            return False, f"Invalid primary_category: {complaint_data['primary_category']}"
        
        # Validate severity enum
        valid_severities = ["low", "medium", "high", "critical"]
        if complaint_data["severity"] not in valid_severities:
            return False, f"Invalid severity: {complaint_data['severity']}"
        
        # Validate confidence range
        if not (0 <= complaint_data["confidence"] <= 1):
            return False, "Confidence must be between 0 and 1"
        
        return True, None
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def is_complaint_trigger(text: str) -> bool:
    """
    Check if user input contains complaint trigger patterns
    
    Args:
        text: User input string
        
    Returns:
        bool: True if complaint trigger detected
    """
    for pattern in config.COMPLAINT_TRIGGERS:
        if re.search(pattern, text):
            return True
    return False


def calculate_confidence(complaint_data: Dict[str, Any]) -> float:
    """
    Calculate confidence score for complaint classification
    
    Args:
        complaint_data: Complaint dictionary
        
    Returns:
        float: Confidence score between 0 and 1
    """
    score = 0.5  # Base confidence
    
    # Increase confidence if key fields are well-populated
    if complaint_data.get("user_intent") and len(complaint_data["user_intent"]) > 20:
        score += 0.1
    
    if complaint_data.get("observed_outcome") and len(complaint_data["observed_outcome"]) > 20:
        score += 0.1
    
    if complaint_data.get("context"):
        score += 0.05
    
    # Increase confidence if categorization found strong keyword matches
    primary_cat = complaint_data.get("primary_category", "other")
    if primary_cat != "other":
        score += 0.15
    
    if complaint_data.get("secondary_categories"):
        score += 0.1
    
    return min(score, 1.0)


def extract_keywords(text: str) -> list[str]:
    """
    Extract important keywords from text
    
    Args:
        text: Input text
        
    Returns:
        list: Keywords found
    """
    text_lower = text.lower()
    keywords = []
    
    # Check all category keywords
    for category, info in config.PRIMARY_CATEGORIES.items():
        for keyword in info["keywords"]:
            if keyword in text_lower:
                keywords.append(keyword)
    
    return list(set(keywords))


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format datetime to ISO 8601 string
    
    Args:
        dt: Datetime object (uses current time if None)
        
    Returns:
        str: ISO formatted timestamp
    """
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """
    Parse ISO 8601 timestamp string to datetime
    
    Args:
        timestamp_str: ISO formatted timestamp
        
    Returns:
        datetime or None if parsing fails
    """
    try:
        return datetime.fromisoformat(timestamp_str)
    except:
        return None


def get_complaint_file_path(complaint_id: str) -> Path:
    """
    Get the file path for a complaint based on its ID
    
    Args:
        complaint_id: Complaint identifier
        
    Returns:
        Path: Full path to complaint JSON file
    """
    # Extract date from ID (format: CMP-YYYY-MM-DD-XXXXXX)
    match = re.match(r'CMP-(\d{4})-(\d{2})-(\d{2})-[A-Z0-9]{6}', complaint_id)
    if match:
        year, month, day = match.groups()
        dir_path = config.COMPLAINTS_DIR / year / month
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path / f"{complaint_id}.json"
    else:
        # Fallback to root complaints directory
        return config.COMPLAINTS_DIR / f"{complaint_id}.json"


def add_audit_entry(complaint_data: Dict[str, Any], actor: str, action: str) -> Dict[str, Any]:
    """
    Add an entry to the complaint's audit trail
    
    Args:
        complaint_data: Complaint dictionary
        actor: Who performed the action
        action: What action was performed
        
    Returns:
        Updated complaint data
    """
    if "audit_trail" not in complaint_data:
        complaint_data["audit_trail"] = []
    
    entry = {
        "timestamp": format_timestamp(),
        "actor": actor,
        "action": action
    }
    
    complaint_data["audit_trail"].append(entry)
    return complaint_data


def sanitize_text(text: str, max_length: int = 2000) -> str:
    """
    Sanitize and truncate text input
    
    Args:
        text: Input text
        max_length: Maximum allowed length
        
    Returns:
        str: Sanitized text
    """
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Truncate if needed
    if len(text) > max_length:
        text = text[:max_length-3] + "..."
    
    return text


def get_severity_emoji(severity: str) -> str:
    """
    Get emoji representation for severity level
    
    Args:
        severity: Severity level
        
    Returns:
        str: Emoji
    """
    emoji_map = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢"
    }
    return emoji_map.get(severity, "⚪")


def format_complaint_summary(complaint_data: Dict[str, Any]) -> str:
    """
    Create a human-readable summary of a complaint
    
    Args:
        complaint_data: Complaint dictionary
        
    Returns:
        str: Formatted summary
    """
    severity_emoji = get_severity_emoji(complaint_data.get("severity", "low"))
    category_emoji = config.PRIMARY_CATEGORIES.get(
        complaint_data.get("primary_category", "other"), {}
    ).get("emoji", "❓")
    
    summary = f"""
{category_emoji} Complaint {complaint_data.get('complaint_id', 'N/A')}
{severity_emoji} Severity: {complaint_data.get('severity', 'N/A').upper()}
📊 Category: {complaint_data.get('primary_category', 'N/A')}
📅 Reported: {complaint_data.get('reported_at', 'N/A')}
🔄 Status: {complaint_data.get('status', 'N/A')}

Intent: {complaint_data.get('user_intent', 'N/A')}
Observed: {complaint_data.get('observed_outcome', 'N/A')}
Expected: {complaint_data.get('expected_outcome', 'N/A')}
"""
    return summary.strip()
