"""
Pydantic model for clarify_issue node output.
"""
from pydantic import BaseModel, Field
from typing import Literal


class ClarifyOutput(BaseModel):
    """
    Structured output from the clarify_issue node.
    
    This model defines the analysis result and determines workflow direction.
    """
    needs_clarification: bool = Field(
        description="Whether the user's input needs more clarification"
    )
    
    response: str = Field(
        description="Either a clarifying question or confirmation to proceed"
    )
    
    reasoning: str = Field(
        description="Brief explanation of why clarification is or isn't needed"
    )
    
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence level in the clarity assessment (0.0 to 1.0)"
    )