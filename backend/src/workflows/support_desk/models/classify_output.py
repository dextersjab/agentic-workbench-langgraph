"""
Pydantic model for classify_issue node output.
"""

from pydantic import BaseModel, Field
from typing import Optional
from src.workflows.support_desk.business_context import (
    IssueCategoryType,
    IssuePriorityType,
)


class ClassifyOutput(BaseModel):
    """
    Structured output from the classify_issue node.

    This model defines the issue classification and priority, and determines
    if more information is needed for proper classification.
    """

    needs_clarification: bool = Field(
        description="Whether more information is needed to properly classify the issue"
    )

    user_requested_escalation: bool = Field(
        default=False,
        description="Whether the user has requested to speak to a human or escalate the issue",
    )

    category: Optional[IssueCategoryType] = Field(
        default=None, description="Primary category of the IT issue (None if uncertain)"
    )

    priority: Optional[IssuePriorityType] = Field(
        default=None,
        description="Priority level based on urgency and impact (None if uncertain)",
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence level in the classification (0.0 to 1.0)",
    )

    reasoning: str = Field(
        description="Brief explanation of the classification decision"
    )
