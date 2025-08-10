"""
Basic company configuration for Support Desk workflow.

This contains only the minimal company information needed that doesn't belong in ontologies.
"""

COMPANY_INFO = {
    "name": "Example Corp",
    "support_hours": "24/7",
    "support_email": "support@company.com",
    "support_phone": "1-800-SUPPORT",
    "ticket_portal": "https://support.company.com"
}

# Support team contact information (extends ontology-based team definitions)
COMPANY_SUPPORT_TEAMS = {
    "L1": {
        "name": "Level 1 Support",
        "description": "First line support for common issues",
        "response_time_hours": 2,
        "resolution_time_hours": 4,
        "contact": {
            "email": "helpdesk@company.com",
            "phone": "1-800-HELP-001",
            "portal": "https://support.company.com/helpdesk"
        }
    },
    "L2": {
        "name": "Level 2 Support", 
        "description": "Technical support for complex issues",
        "response_time_hours": 4,
        "resolution_time_hours": 8,
        "contact": {
            "email": "technical@company.com",
            "phone": "1-800-TECH-002",
            "portal": "https://support.company.com/technical"
        }
    },
    "escalation": {
        "name": "Escalation Team",
        "description": "Senior technical staff for critical issues",
        "response_time_hours": 1,
        "resolution_time_hours": 4,
        "contact": {
            "email": "escalations@company.com",
            "phone": "1-800-ESCL-003",
            "portal": "https://support.company.com/escalations"
        }
    },
    "specialist": {
        "name": "Specialist Team",
        "description": "Domain experts for specific technologies",
        "response_time_hours": 8,
        "resolution_time_hours": 24,
        "contact": {
            "email": "specialists@company.com",
            "phone": "1-800-SPEC-004",
            "portal": "https://support.company.com/specialists"
        }
    }
}