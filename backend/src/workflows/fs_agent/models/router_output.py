"""Router output model for fs_agent workflow."""
from typing import Optional
from pydantic import BaseModel, Field


class RouterOutput(BaseModel):
    """Structured output for router decision."""
    is_read_only: bool = Field(
        ...,
        description="True if only read operations are needed, False if write operations are needed"
    )
    reasoning: Optional[str] = Field(
        None,
        description="Brief explanation of the routing decision"
    )