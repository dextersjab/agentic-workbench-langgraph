"""
Pydantic model for gather_info iterative questioning.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class GatherQuestionOutput(BaseModel):
    """
    Structured output for gather_info iterative questioning.
    
    This model defines what information is still needed and what question to ask next.
    """
    missing_info_categories: List[str] = Field(
        description="Categories of information still needed (e.g., 'device_details', 'timeline', 'user_impact')"
    )
    
    next_question: str = Field(
        description="The specific question to ask the user to gather missing information"
    )
    
    is_gathering_complete: bool = Field(
        description="True if all necessary information has been gathered, False if more questions needed"
    )
    
    gathered_info_summary: str = Field(
        default="",
        description="Summary of information gathered so far (empty string if gathering not complete)"
    )
    
    confidence_score: float = Field(
        description="Confidence that we have sufficient information (0.0 to 1.0)"
    )
    
    response: str = Field(
        description="User-facing message asking the specific question"
    )