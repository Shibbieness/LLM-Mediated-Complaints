"""
Configuration file for LLM-Mediated Complaint System
Contains all system constants, paths, and configuration parameters
"""

import os
from pathlib import Path

# System Version
VERSION = "1.0.0"
SYSTEM_NAME = "LLM-Mediated Complaint Intake System"

# File Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "complaint_data"
COMPLAINTS_DIR = DATA_DIR / "complaints"
INDICES_DIR = DATA_DIR / "indices"
SCHEMA_PATH = BASE_DIR / "complaint_schema.json"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
COMPLAINTS_DIR.mkdir(exist_ok=True)
INDICES_DIR.mkdir(exist_ok=True)

# Complaint Trigger Patterns
COMPLAINT_TRIGGERS = [
    r"(?i)\b(file|submit|make|log)\s+(a\s+)?complaint\b",
    r"(?i)\bi\s+want\s+to\s+complain\b",
    r"(?i)\bthis\s+(isn't|is\s+not|doesn't)\s+work",
    r"(?i)\breport\s+(a\s+)?(bug|issue|problem)\b",
    r"(?i)\bsomething\s+(went\s+)?wrong\b",
    r"(?i)\bnot\s+working\b",
    r"(?i)\bbroken\b"
]

# Category Definitions
PRIMARY_CATEGORIES = {
    "bug": {
        "emoji": "🐞",
        "description": "System malfunction or technical error",
        "keywords": ["crash", "freeze", "error", "broken", "not working", "failed"]
    },
    "model_behavior": {
        "emoji": "🤖",
        "description": "AI model not behaving as expected",
        "keywords": ["ignored", "verbose", "wrong tone", "hallucination", "repetition", 
                     "misunderstood", "constraint", "overwrite", "replace"]
    },
    "ux_ui": {
        "emoji": "🖥",
        "description": "User interface or experience issue",
        "keywords": ["confusing", "hidden", "can't find", "unclear", "difficult to use"]
    },
    "feature_request": {
        "emoji": "💡",
        "description": "Request for new capability",
        "keywords": ["need", "want", "would be nice", "suggestion", "could you add"]
    },
    "policy_friction": {
        "emoji": "📜",
        "description": "Issue with system restrictions or policies",
        "keywords": ["won't let me", "refused", "blocked", "not allowed", "restricted"]
    },
    "performance": {
        "emoji": "🚀",
        "description": "Speed or latency issue",
        "keywords": ["slow", "timeout", "lag", "taking forever", "performance"]
    },
    "trust_safety": {
        "emoji": "🔐",
        "description": "Privacy or security concern",
        "keywords": ["privacy", "security", "data", "unsafe", "concern"]
    },
    "misunderstanding": {
        "emoji": "🧠",
        "description": "Confusion about how something works",
        "keywords": ["confused", "don't understand", "how do", "what does"]
    },
    "other": {
        "emoji": "❓",
        "description": "Uncategorized complaint",
        "keywords": []
    }
}

# Severity Indicators
SEVERITY_INDICATORS = {
    "critical": {
        "keywords": ["impossible", "can't work", "completely broken", "unusable", 
                     "critical", "urgent", "emergency"],
        "score_threshold": 4
    },
    "high": {
        "keywords": ["broken", "can't", "won't", "always", "never", "job", "work"],
        "score_threshold": 3
    },
    "medium": {
        "keywords": ["difficult", "frustrating", "sometimes", "often", "annoying"],
        "score_threshold": 1
    },
    "low": {
        "keywords": ["minor", "small", "slight", "occasionally"],
        "score_threshold": 0
    }
}

# Root Cause Indicators
ROOT_CAUSE_PATTERNS = {
    "constraint_parsing_failure": ["ignored constraint", "didn't follow", "overwrite", 
                                    "replaced", "append"],
    "context_overload": ["long conversation", "forgot", "earlier"],
    "ambiguous_instructions": ["unclear", "confused", "not sure what"],
    "model_overcorrection": ["too cautious", "overly", "excessive"],
    "system_bug": ["crash", "error", "freeze", "failed"],
    "latency_issue": ["slow", "timeout", "lag"],
    "ui_confusion": ["couldn't find", "where is", "how do"],
    "policy_boundary": ["won't let me", "refused", "blocked"],
    "hallucination": ["made up", "incorrect", "wrong information", "fabricated"],
    "data_absence": ["don't know", "no information", "can't find"]
}

# Routing Rules
ROUTING_RULES = {
    "self_correction": {
        "conditions": ["model_behavior", "constraint_parsing_failure"],
        "severity_max": "high"
    },
    "human_review": {
        "conditions": ["critical"],
        "categories": ["bug", "trust_safety"]
    },
    "product_backlog": {
        "conditions": ["feature_request"],
        "severity_min": "medium"
    },
    "safety_escalation": {
        "conditions": ["trust_safety", "policy_boundary"],
        "severity_min": "high"
    },
    "documentation_update": {
        "conditions": ["misunderstanding"],
        "frequency": "persistent"
    }
}

# Conversation Settings
MAX_CLARIFICATION_ROUNDS = 3
CONFIDENCE_THRESHOLD = 0.6
SIMILARITY_THRESHOLD = 0.75

# Question Templates
INTAKE_QUESTIONS = {
    "user_intent": [
        "What were you trying to accomplish?",
        "What was your goal?",
        "What were you attempting to do?"
    ],
    "observed_outcome": [
        "What actually happened?",
        "What went wrong?",
        "What was the result?"
    ],
    "expected_outcome": [
        "What did you expect to happen?",
        "What should have happened?",
        "What was the intended result?"
    ],
    "incident_at": [
        "When did this occur?",
        "What time did this happen?",
        "How recently was this?"
    ],
    "frequency": [
        "How often has this happened?",
        "Is this a recurring issue?",
        "How many times have you encountered this?"
    ],
    "context": [
        "Can you provide any additional context?",
        "What else should I know?",
        "Are there any other relevant details?"
    ]
}

# Status Transitions
VALID_STATUS_TRANSITIONS = {
    "new": ["triaged"],
    "triaged": ["structured"],
    "structured": ["clustered"],
    "clustered": ["routed"],
    "routed": ["in_progress"],
    "in_progress": ["resolved", "awaiting_user"],
    "awaiting_user": ["in_progress", "resolved"],
    "resolved": ["closed"],
    "closed": ["reopened"],
    "reopened": ["triaged"]
}
