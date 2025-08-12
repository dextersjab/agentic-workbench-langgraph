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

# Required information categories for ticket creation
REQUIRED_INFO_CATEGORIES = {
    "device_system": {
        "name": "Device/System Details",
        "description": "Specific hardware/software involved, models, versions"
    },
    "timeline": {
        "name": "Timeline", 
        "description": "When did this start, frequency, patterns"
    },
    "user_impact": {
        "name": "User Impact",
        "description": "How this affects work, urgency, business impact"
    },
    "symptoms": {
        "name": "Symptoms",
        "description": "Specific error messages, behaviors, what exactly happens"
    },
    "context": {
        "name": "Context",
        "description": "What user was doing when issue occurred, recent changes"
    },
    "environment": {
        "name": "Environment", 
        "description": "User location, department, role (if relevant to issue)"
    }
}

# Category-specific information priorities for ServiceHub environment
CATEGORY_SPECIFIC_PRIORITIES = {
    "hardware": {
        "name": "Hardware",
        "priorities": "Device models, physical symptoms, connectivity (Dell/Lenovo equipment)"
    },
    "software": {
        "name": "Software", 
        "priorities": "Application versions, error messages, affected workflows (ServiceHub Portal, Dynamics 365, Salesforce CRM, Azure AD)"
    },
    "access": {
        "name": "Access",
        "priorities": "Account names, systems, permission levels (consider department-specific procedures)"
    },
    "network": {
        "name": "Network",
        "priorities": "Connection types, locations, affected devices (London HQ, Manchester, Edinburgh, remote workers)"
    }
}

def format_required_info_categories() -> str:
    """Format required information categories as markdown."""
    lines = ["## Required Information Categories", ""]
    for i, category in enumerate(REQUIRED_INFO_CATEGORIES.values(), 1):
        lines.append(f"{i}. **{category['name']}**: {category['description']}")
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
        lines.append(f"- **{priority['name']}**: {priority['priorities']}")
    return "\n".join(lines)