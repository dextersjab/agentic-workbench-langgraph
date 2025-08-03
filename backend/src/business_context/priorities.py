"""Company-wide priority definitions and classification rules"""

SCHEMA_VERSION = "1.0"

# Unified priority configuration combining definitions, SLA times, and multipliers
PRIORITY_CONFIG = {
    "P1": {
        "name": "Critical",
        "description": "System outages affecting >50 users, security breaches, data loss",
        "response_hours": 1,
        "resolution_hours": 4,
        "multiplier": 1.0,  # No multiplier, 24/7 response
        "examples": ["System outages", "Security breaches", "Data loss", "Payroll system failures"]
    },
    "P2": {
        "name": "High", 
        "description": "Individual unable to work, failed hardware, access lockouts",
        "response_hours": 4,
        "resolution_hours": 24,
        "multiplier": 1.5,  # 50% more time during business hours
        "examples": ["Individual unable to work", "Failed hardware", "Access lockouts", "VPN connectivity issues"]
    },
    "P3": {
        "name": "Medium",
        "description": "Performance issues, software requests, password resets",
        "response_hours": 24,
        "resolution_hours": 72,
        "multiplier": 2.0,  # Double time, business hours only
        "examples": ["Performance issues", "Software requests", "Password resets", "Slow response times"]
    },
    "P4": {
        "name": "Low",
        "description": "How-to questions, feature requests, training needs",
        "response_hours": 48,
        "resolution_hours": 120,
        "multiplier": 3.0,  # Triple time, business hours only
        "examples": ["How-to questions", "Feature requests", "Training needs", "General inquiries"]
    }
}