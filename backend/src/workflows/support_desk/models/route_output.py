"""
Pydantic model for route_issue node output.
"""

from pydantic import BaseModel, Field
from typing import Literal


class RouteOutput(BaseModel):
    """
    Structured output from the route_issue node.

    This model defines the team assignment and routing information.
    """

    support_team: Literal["L1", "L2", "specialist", "escalation"] = Field(
        description="Assigned support team based on category and priority"
    )

    estimated_resolution_time: str = Field(
        description="Expected resolution timeframe (e.g., '2 hours', '1 business day')"
    )

    escalation_path: str = Field(
        description="Next escalation level if L1 cannot resolve"
    )
