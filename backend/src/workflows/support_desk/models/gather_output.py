"""
Pydantic model for gather_info node output.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List


class GatherOutput(BaseModel):
    """
    Structured output from the gather_info node.

    This model defines the comprehensive ticket information.
    """

    ticket_summary: str = Field(
        description="Concise summary of the issue for ticket title"
    )

    detailed_description: str = Field(
        description="Comprehensive description of the issue and context"
    )

    affected_systems: List[str] = Field(
        default_factory=list,
        description="List of systems, applications, or hardware affected",
    )

    user_impact: str = Field(
        description="Description of how the issue impacts the user's work"
    )

    reproduction_steps: List[str] = Field(
        default_factory=list, description="Steps to reproduce the issue, if applicable"
    )

    additional_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context like user role, department, location, etc.",
    )

    response: str = Field(
        description="User-facing message summarizing the information gathered"
    )
