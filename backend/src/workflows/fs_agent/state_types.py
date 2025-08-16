"""State type definitions for fs_agent workflow using TypedDict."""
from typing import List, Dict, Any, Literal, Optional
from typing_extensions import TypedDict


class FileAction(TypedDict):
    """Represents a file action to be performed."""
    action_type: Literal["list", "read", "write", "delete"]
    path: str
    content: Optional[str]  # Only for write actions


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


class ActionState(TypedDict):
    """State related to current action execution."""
    planned_action: Optional[FileAction]
    action_result: Optional[ActionResult]
    action_counter: Dict[str, int]  # Track repeated actions


class FSAgentState(TypedDict):
    """
    Composed state for the fs_agent workflow.
    
    This state uses composition to group related fields for better organization.
    """
    messages: List[Dict[str, str]]  # Chat messages in OpenAI format
    session: SessionState
    action: ActionState