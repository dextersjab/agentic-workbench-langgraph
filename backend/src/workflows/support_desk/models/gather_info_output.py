"""
Pydantic model for gather_info node output.
"""
from pydantic import BaseModel, Field
from typing import List


class GatherInfoOutput(BaseModel):
    """
    Structured output from the gather_info node.
    
    This model defines whether more information is needed and provides
    the appropriate response to the user.
    """
    needs_more_info: bool = Field(
        description="Whether more information is needed from the user"
    )
    
    response: str | None = Field(
        default=None,
        description="Targeted question when more info is needed, None when sufficient info is available"
    )
    
    reasoning: str = Field(
        description="Brief explanation of why more info is or isn't needed"
    )
    
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence level in the information sufficiency assessment (0.0 to 1.0)"
    )
    
    gathering_complete: bool = Field(
        description="Whether the information gathering process should be considered complete"
    )
    
    missing_categories: List[str] = Field(
        default_factory=list,
        description="Categories of information still missing (e.g., 'device_details', 'timeline')"
    )