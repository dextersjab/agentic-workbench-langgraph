"""Business context and domain knowledge for IT Support Desk workflow

This module contains the business rules and domain expertise specific to 
the IT Support Desk workflow. It extends company-wide definitions with
workflow-specific categorizations and rules.
"""

SCHEMA_VERSION = "1.0"

from typing import Literal
from src.business_context import COMPANY_SUPPORT_TEAMS, BASE_SLA_POLICIES, PRIORITY_CONFIG

# Maximum number of information gathering rounds before proceeding to ticket creation
MAX_GATHERING_ROUNDS = 2

# Type definitions for issue classification
IssueCategoryType = Literal["hardware", "software", "access", "network", "other"]
IssuePriorityType = Literal["P1", "P2", "P3", "P4"]

# Workflow-specific issue categorizations
ISSUE_CATEGORIES = {
    "hardware": {
        "keywords": ["laptop", "desktop", "printer", "phone", "keyboard", "mouse", "monitor"],
        "typical_team": "L1",
        "escalation_triggers": ["multiple devices", "data loss", "executive user"]
    },
    "software": {
        "keywords": ["application", "app", "software", "program", "crash", "error", "bug"],
        "typical_team": "L1",
        "escalation_triggers": ["business critical", "affects multiple users", "data corruption"]
    },
    "access": {
        "keywords": ["password", "login", "vpn", "permissions", "account", "locked out"],
        "typical_team": "L1", 
        "escalation_triggers": ["security breach", "compliance issue", "system-wide"]
    },
    "network": {
        "keywords": ["internet", "wifi", "connection", "network", "slow", "bandwidth"],
        "typical_team": "L2",
        "escalation_triggers": ["complete outage", "affects whole floor/building"]
    },
    "other": {
        "keywords": [],
        "typical_team": "L1",
        "escalation_triggers": []
    }
}

# Extend company teams with workflow-specific definitions
SUPPORT_TEAMS = {
    **COMPANY_SUPPORT_TEAMS
}

# Workflow-specific routing rules
ROUTING_RULES = {
    "auto_escalate_keywords": ["urgent", "critical", "CEO", "compliance", "security breach"],
    "specialist_triggers": {
        "salesforce": "CRM Specialist",
        "sap": "ERP Specialist", 
        "azure": "Cloud Specialist",
        "security": "Security Specialist"
    }
}

# Knowledge base categories for this workflow
KB_CATEGORIES = [
    "getting_started",
    "common_issues", 
    "troubleshooting",
    "how_to_guides",
    "policies"
]

# Workflow-specific SLA commitments (derived from company policies)
def get_sla_commitment(priority: str) -> tuple[str, int]:
    """
    Get SLA commitment for support desk based on priority and company policies.
    
    Args:
        priority: Issue priority (P1, P2, P3, P4)
        
    Returns:
        Tuple of (SLA description, hours)
    """
    if priority not in PRIORITY_CONFIG:
        priority = "P3"  # Default to medium priority
    
    priority_info = PRIORITY_CONFIG[priority]
    base_hours = priority_info["resolution_hours"]
    multiplier = priority_info["multiplier"]
    
    # Apply business hours multiplier for non-critical issues
    if priority != "P1":
        adjusted_hours = int(base_hours * multiplier / 2.0)  # Normalize multiplier
    else:
        adjusted_hours = base_hours  # Critical issues get full 24/7 commitment
    
    return (f"{adjusted_hours} hours", adjusted_hours)

# SLA mapping for quick lookup
SLA_COMMITMENTS = {
    priority: get_sla_commitment(priority) 
    for priority in PRIORITY_CONFIG.keys()
}