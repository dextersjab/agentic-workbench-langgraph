"""
Pydantic model for information completeness check output.
"""
from pydantic import BaseModel, Field


class InfoCompletenessOutput(BaseModel):
    """
    Structured output for checking if enough information has been gathered.
    
    This model determines whether we have sufficient information to create
    a comprehensive support ticket or need to gather more details.
    """
    needs_more_info: bool = Field(
        description="True if more information is needed, False if sufficient for ticket creation"
    )
    
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence level in the completeness assessment (0.0 to 1.0)"
    )
    
    missing_categories: list[str] = Field(
        default=[],
        description="Categories of information still needed (e.g., 'device_details', 'timeline', 'user_impact')"
    )
    
    reasoning: str = Field(
        description="Brief explanation of why more info is/isn't needed"
    )
    
    response: str = Field(
        description="Internal assessment message (not shown to user)"
    )