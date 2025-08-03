"""Company-wide SLA policies and commitments"""

SCHEMA_VERSION = "1.0"

BASE_SLA_POLICIES = {
    "priority_multipliers": {
        "P1": 1.0,   # Critical - no multiplier
        "P2": 1.5,   # High - 50% more time
        "P3": 2.0,   # Medium - double time
        "P4": 3.0    # Low - triple time
    },
    "business_hours": {
        "start": "09:00",
        "end": "17:00",
        "timezone": "UTC",
        "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    }
}