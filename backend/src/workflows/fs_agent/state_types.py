"""State type definitions for fs_agent workflow using TypedDict."""

from typing import List, Dict, Any, Literal, Optional
from typing_extensions import TypedDict


class EditOperation(TypedDict):
    """Represents a single edit operation on a file."""

    line_number: Optional[int]  # Line to edit, None for append
    old_content: Optional[str]  # Expected content for replacement, None for new lines
    new_content: str  # New content to insert/replace


class FileAction(TypedDict):
    """Represents a file action to be performed."""

    action_type: Literal["list", "read", "write", "edit", "delete"]
    path: str
    content: Optional[str]  # For write actions
    edits: Optional[List[EditOperation]]  # For edit actions


class ActionResult(TypedDict):
    """Represents the result of a file action."""

    success: bool
    result: Optional[Any]  # File content, file list, etc.
    error: Optional[str]


class SessionState(TypedDict):
    """State related to the session configuration."""

    working_directory: str
    is_read_only: bool
    is_finished: bool
    is_first_interaction: bool  # Track if this is the first user message


class ActionState(TypedDict):
    """State related to current action execution."""

    planned_action: Optional[FileAction]
    action_result: Optional[ActionResult]
    action_counter: Dict[str, int]  # Track repeated actions


class PlanningState(TypedDict):
    """State related to reasoning and planning iterations."""

    thinking_iterations: int  # Current thinking iteration count
    needs_deeper_thinking: bool  # Whether the agent wants to think more
    current_reasoning: str  # Current reasoning/thoughts
    alternative_approaches: List[str]  # Alternative approaches considered


class ApprovalState(TypedDict):
    """State related to human approval for risky operations."""

    needs_approval: bool  # Whether current action needs approval
    approval_granted: bool  # Whether user approved the action
    preview_content: str  # Diff or preview content for approval
    backup_path: Optional[str]  # Path to backup file for rollback


class FSAgentState(TypedDict):
    """
    Composed state for the fs_agent workflow.

    This state uses composition to group related fields for better organization.
    """

    messages: List[Dict[str, str]]  # Chat messages in OpenAI format
    session: SessionState
    action: ActionState
    planning: PlanningState
    approval: ApprovalState
