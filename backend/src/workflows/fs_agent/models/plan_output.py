"""Plan output model for fs_agent workflow."""
from typing import Optional, Literal, List
from pydantic import BaseModel, Field

from .observe_output import FileActionModel


class PlanOutput(BaseModel):
    """Structured output for planning and reasoning."""
    reasoning: str = Field(
        ...,
        description="The agent's reasoning and thought process"
    )
    needs_deeper_thinking: bool = Field(
        False,
        description="Whether the agent needs to think more deeply about the problem"
    )
    planned_action: Optional[FileActionModel] = Field(
        None,
        description="The planned file action to execute, or None if more thinking is needed"
    )
    alternative_approaches: List[str] = Field(
        default_factory=list,
        description="Alternative approaches considered"
    )
    confidence_level: Literal["low", "medium", "high"] = Field(
        "medium",
        description="How confident the agent is in its current plan"
    )
    is_finished: bool = Field(
        False,
        description="True if the user's request has been completely fulfilled"
    )