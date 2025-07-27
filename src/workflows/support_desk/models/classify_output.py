"""
Pydantic model for classify_issue node output.
"""
from pydantic import BaseModel, Field
from typing import Literal


class ClassifyOutput(BaseModel):
    """
    Structured output from the classify_issue node.
    
    This model defines the issue classification and priority, and determines
    if more information is needed for proper classification.
    """
    needs_clarification: bool = Field(
        description="Whether more information is needed to properly classify the issue"
    )
    
    category: Literal["hardware", "software", "access", "network", "other"] = Field(
        description="Primary category of the IT issue"
    )
    
    priority: Literal["P1", "P2", "P3"] = Field(
        description="Priority level based on urgency and impact"
    )
    
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence level in the classification (0.0 to 1.0)"
    )
    
    reasoning: str = Field(
        description="Brief explanation of the classification decision"
    )
    
    response: str = Field(
        description="User-facing message - either classification summary or clarifying question"
    )