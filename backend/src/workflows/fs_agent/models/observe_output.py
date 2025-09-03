"""Observe output model for fs_agent workflow."""
from typing import Optional, Literal, List
from pydantic import BaseModel, Field


class EditOperationModel(BaseModel):
    """Represents a single edit operation."""
    line_number: Optional[int] = Field(
        None,
        description="Line number to edit (1-based), None for append"
    )
    old_content: Optional[str] = Field(
        None,
        description="Expected content to replace, None for new lines"
    )
    new_content: str = Field(
        ...,
        description="New content to insert or replace with"
    )


class FileActionModel(BaseModel):
    """Represents a planned file action."""
    action_type: Literal["list", "read", "write", "edit", "delete"] = Field(
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
    edits: Optional[List[EditOperationModel]] = Field(
        None,
        description="Edit operations to perform (only for edit actions)"
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
    is_read_only: Optional[bool] = Field(
        None,
        description="True if only read operations are needed, False if write operations are needed (only set on first interaction)"
    )
    message: Optional[str] = Field(
        None,
        description="Optional message to provide context about the action"
    )