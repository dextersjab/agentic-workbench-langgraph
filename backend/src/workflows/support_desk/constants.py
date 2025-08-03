"""
Support Desk workflow constants.

Simple constants for workflow behavior configuration.
"""
from typing import Literal

# Maximum number of information gathering rounds before proceeding to ticket creation
MAX_GATHERING_ROUNDS = 2

# Type definitions for issue classification
IssueCategoryType = Literal["hardware", "software", "access", "network", "other"]
IssuePriorityType = Literal["P1", "P2", "P3"]