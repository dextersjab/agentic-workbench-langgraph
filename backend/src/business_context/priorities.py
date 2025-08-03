"""Company-wide priority definitions and classification rules"""

PRIORITY_DEFINITIONS = {
    "P1": {
        "name": "Critical",
        "description": "System outages affecting >50 users, security breaches, data loss",
        "response_time_hours": 1,
        "resolution_time_hours": 4,
        "examples": ["System outages", "Security breaches", "Data loss", "Payroll system failures"]
    },
    "P2": {
        "name": "High", 
        "description": "Individual unable to work, failed hardware, access lockouts",
        "response_time_hours": 4,
        "resolution_time_hours": 24,
        "examples": ["Individual unable to work", "Failed hardware", "Access lockouts", "VPN connectivity issues"]
    },
    "P3": {
        "name": "Medium",
        "description": "Performance issues, software requests, password resets",
        "response_time_hours": 24,
        "resolution_time_hours": 72,
        "examples": ["Performance issues", "Software requests", "Password resets", "Slow response times"]
    },
    "P4": {
        "name": "Low",
        "description": "How-to questions, feature requests, training needs",
        "response_time_hours": 48,
        "resolution_time_hours": 120,
        "examples": ["How-to questions", "Feature requests", "Training needs", "General inquiries"]
    }
}

# Business hours multiplier for SLA calculations
BUSINESS_HOURS_MULTIPLIER = {
    "P1": 1.0,   # Critical - no multiplier, 24/7 response
    "P2": 1.5,   # High - 50% more time during business hours
    "P3": 2.0,   # Medium - double time, business hours only
    "P4": 3.0    # Low - triple time, business hours only
}