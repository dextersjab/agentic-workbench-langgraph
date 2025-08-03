"""Company-wide support team definitions"""

COMPANY_SUPPORT_TEAMS = {
    "L1": {
        "name": "Level 1 Support",
        "description": "First line support for common issues",
        "response_time_hours": 2,
        "resolution_time_hours": 4
    },
    "L2": {
        "name": "Level 2 Support", 
        "description": "Technical support for complex issues",
        "response_time_hours": 4,
        "resolution_time_hours": 8
    },
    "escalation": {
        "name": "Escalation Team",
        "description": "Senior technical staff for critical issues",
        "response_time_hours": 1,
        "resolution_time_hours": 4
    },
    "specialist": {
        "name": "Specialist Team",
        "description": "Domain experts for specific technologies",
        "response_time_hours": 8,
        "resolution_time_hours": 24
    }
}