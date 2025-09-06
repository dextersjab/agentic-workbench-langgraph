"""fs_agent workflow state management."""
from typing import TypeVar
from pydantic import BaseModel

from .state_types import SessionState, ActionState, PlanningState, ApprovalState, FSAgentState

T = TypeVar('T', bound=BaseModel)


def create_initial_state() -> FSAgentState:
    """
    Create initial composed state for fs_agent workflow.
    
    Returns:
        A new FSAgentState with default values using composition.
    """
    return FSAgentState(
        messages=[],
        session=SessionState(
            working_directory="./workspace",
            is_read_only=True,
            is_finished=False,
            is_first_interaction=True
        ),
        action=ActionState(
            planned_action=None,
            action_result=None,
            action_counter={}
        ),
        planning=PlanningState(
            thinking_iterations=0,
            needs_deeper_thinking=False,
            current_reasoning="",
            alternative_approaches=[]
        ),
        approval=ApprovalState(
            needs_approval=False,
            approval_granted=False,
            preview_content="",
            backup_path=None
        )
    )