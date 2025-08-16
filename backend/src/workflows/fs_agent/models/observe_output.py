"""Observe output model for fs_agent workflow."""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class FileActionModel(BaseModel):
    """Represents a planned file action."""
    action_type: Literal["list", "read", "write", "delete"] = Field(
        ...,
        description="Type of file operation to perform"
    )
    path: str = Field(
        ...,
        description="Path to the file or directory"
    )
    content: Optional[str] = Field(
        None,
        description="Content to write (only for write actions)"
    )


class ObserveOutput(BaseModel):
    """Structured output for observation and planning."""
    planned_action: Optional[FileActionModel] = Field(
        None,
        description="The next file action to perform, or None if finished"
    )
    is_finished: bool = Field(
        False,
        description="True if the user's request has been fulfilled"
    )
    message: Optional[str] = Field(
        None,
        description="Optional message to provide context about the action"
    )