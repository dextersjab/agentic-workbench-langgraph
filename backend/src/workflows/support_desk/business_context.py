"""Business context and domain knowledge for IT Support Desk workflow

This module contains the business rules and domain expertise specific to 
the IT Support Desk workflow. It extends company-wide definitions with
workflow-specific categorizations and rules.
"""

SCHEMA_VERSION = "1.0"

from typing import Literal
from .config.company_config import COMPANY_SUPPORT_TEAMS
from .utils import load_ontologies, get_sla_commitment as ontology_get_sla_commitment

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

# Load priority ontology for SLA calculations
_, priorities_ontology, _ = load_ontologies()

# Workflow-specific SLA commitments (using priority ontology)
def get_sla_commitment(priority: str) -> tuple[str, int]:
    """
    Get SLA commitment for support desk based on priority ontology.
    
    Args:
        priority: Issue priority (P1, P2, P3, P4)
        
    Returns:
        Tuple of (SLA description, hours)
    """
    return ontology_get_sla_commitment(priorities_ontology, priority)

# SLA mapping for quick lookup
SLA_COMMITMENTS = {
    f"P{i}": get_sla_commitment(f"P{i}") 
    for i in range(1, 5)
}

# Deterministic routing table based on category and priority
ROUTING_TABLE = {
    # Hardware issues
    ("hardware", "P1"): {
        "support_team": "L2",
        "estimated_resolution_time": "2 hours",
        "escalation_path": "specialist -> escalation"
    },
    ("hardware", "P2"): {
        "support_team": "L1", 
        "estimated_resolution_time": "4 hours",
        "escalation_path": "L2 -> specialist"
    },
    ("hardware", "P3"): {
        "support_team": "L1",
        "estimated_resolution_time": "1 business day",
        "escalation_path": "L2"
    },
    ("hardware", "P4"): {
        "support_team": "L1",
        "estimated_resolution_time": "3 business days",
        "escalation_path": "L2"
    },
    
    # Software issues
    ("software", "P1"): {
        "support_team": "L2",
        "estimated_resolution_time": "2 hours",
        "escalation_path": "specialist -> escalation"
    },
    ("software", "P2"): {
        "support_team": "L1",
        "estimated_resolution_time": "4 hours", 
        "escalation_path": "L2 -> specialist"
    },
    ("software", "P3"): {
        "support_team": "L1",
        "estimated_resolution_time": "1 business day",
        "escalation_path": "L2"
    },
    ("software", "P4"): {
        "support_team": "L1",
        "estimated_resolution_time": "3 business days",
        "escalation_path": "L2"
    },
    
    # Access issues
    ("access", "P1"): {
        "support_team": "L2",
        "estimated_resolution_time": "1 hour",
        "escalation_path": "specialist -> escalation"
    },
    ("access", "P2"): {
        "support_team": "L1",
        "estimated_resolution_time": "2 hours",
        "escalation_path": "L2 -> specialist"
    },
    ("access", "P3"): {
        "support_team": "L1",
        "estimated_resolution_time": "4 hours",
        "escalation_path": "L2"
    },
    ("access", "P4"): {
        "support_team": "L1",
        "estimated_resolution_time": "1 business day",
        "escalation_path": "L2"
    },
    
    # Network issues
    ("network", "P1"): {
        "support_team": "specialist",
        "estimated_resolution_time": "1 hour",
        "escalation_path": "escalation"
    },
    ("network", "P2"): {
        "support_team": "L2",
        "estimated_resolution_time": "2 hours",
        "escalation_path": "specialist -> escalation"
    },
    ("network", "P3"): {
        "support_team": "L2",
        "estimated_resolution_time": "4 hours",
        "escalation_path": "specialist"
    },
    ("network", "P4"): {
        "support_team": "L1",
        "estimated_resolution_time": "1 business day",
        "escalation_path": "L2 -> specialist"
    },
    
    # Other issues (default routing)
    ("other", "P1"): {
        "support_team": "L2",
        "estimated_resolution_time": "2 hours",
        "escalation_path": "specialist -> escalation"
    },
    ("other", "P2"): {
        "support_team": "L1",
        "estimated_resolution_time": "4 hours",
        "escalation_path": "L2 -> specialist"
    },
    ("other", "P3"): {
        "support_team": "L1",
        "estimated_resolution_time": "1 business day",
        "escalation_path": "L2"
    },
    ("other", "P4"): {
        "support_team": "L1",
        "estimated_resolution_time": "3 business days",
        "escalation_path": "L2"
    }
}

def get_routing_decision(issue_category: str, issue_priority: str, conversation_text: str = "") -> dict:
    """
    Get deterministic routing decision based on category, priority and conversation content.
    
    Args:
        issue_category: The category of the issue
        issue_priority: The priority level of the issue
        conversation_text: Combined text from conversation for keyword analysis
        
    Returns:
        Dictionary with support_team, estimated_resolution_time, and escalation_path
    """
    # Check for auto-escalation keywords
    if conversation_text:
        conversation_lower = conversation_text.lower()
        for keyword in ROUTING_RULES["auto_escalate_keywords"]:
            if keyword.lower() in conversation_lower:
                return {
                    "support_team": "escalation",
                    "estimated_resolution_time": "30 minutes",
                    "escalation_path": "executive"
                }
        
        # Check for specialist triggers
        for trigger, specialist in ROUTING_RULES["specialist_triggers"].items():
            if trigger.lower() in conversation_lower:
                return {
                    "support_team": "specialist", 
                    "estimated_resolution_time": "2 hours",
                    "escalation_path": f"{specialist} -> escalation"
                }
    
    # Use routing table for standard routing
    routing_key = (issue_category or "other", issue_priority or "P2")
    
    # Default fallback if key not found
    default_routing = {
        "support_team": "L1",
        "estimated_resolution_time": "4 hours", 
        "escalation_path": "L2 -> specialist"
    }
    
    return ROUTING_TABLE.get(routing_key, default_routing)

# Required information categories for ticket creation
REQUIRED_INFO_CATEGORIES = {
    "device_system": {
        "name": "Device/System Details",
        "description": ["Specific device make and model", "Software/application name and version", "Operating system version"]
    },
    "timeline": {
        "name": "Timeline", 
        "description": ["When the issue first occurred", "How often it happens (once/intermittent/constant)", "Any patterns or triggers"]
    },
    "user_impact": {
        "name": "User Impact",
        "description": ["Number of users affected", "Business processes blocked", "Severity of productivity impact"]
    },
    "symptoms": {
        "name": "Symptoms",
        "description": ["Exact error messages or codes", "Observable behavior or symptoms", "What happens when attempting the task"]
    },
    "context": {
        "name": "Context",
        "description": ["What was being attempted when issue occurred", "Recent system or environment changes", "Previous troubleshooting attempts"]
    },
    "environment": {
        "name": "Environment", 
        "description": ["Physical location or office", "Network connection type (office/VPN/home)", "User's department and role"]
    }
}

# Category-specific information priorities for ServiceHub environment
CATEGORY_SPECIFIC_PRIORITIES = {
    "hardware": {
        "name": "Hardware",
        "priorities": ["Device models", "Physical symptoms", "Connectivity (Dell/Lenovo equipment)"]
    },
    "software": {
        "name": "Software", 
        "priorities": ["Application versions", "Error messages", "Affected workflows (ServiceHub Portal, Dynamics 365, Salesforce CRM, Azure AD)"]
    },
    "access": {
        "name": "Access",
        "priorities": ["Account names", "Systems", "Permission levels (consider department-specific procedures)"]
    },
    "network": {
        "name": "Network",
        "priorities": ["Connection types", "Locations", "Affected devices (London HQ, Manchester, Edinburgh, remote workers)"]
    }
}

def format_required_info_categories() -> str:
    """Format required information categories as markdown."""
    lines = ["## Required Information Categories", ""]
    for i, category in enumerate(REQUIRED_INFO_CATEGORIES.values(), 1):
        desc_items = ", ".join(category['description'])
        lines.append(f"{i}. **{category['name']}**: {desc_items}")
    return "\n".join(lines)

def format_category_specific_priorities(issue_category: str) -> str:
    """Format category-specific priorities as markdown."""
    lines = [
        "## Category-Specific Priorities",
        "",
        f"For **{issue_category}** issues in ServiceHub's environment, prioritize:",
        ""
    ]
    for priority in CATEGORY_SPECIFIC_PRIORITIES.values():
        priority_items = ", ".join(priority['priorities'])
        lines.append(f"- **{priority['name']}**: {priority_items}")
    return "\n".join(lines)