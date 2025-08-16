"""fs_agent workflow state management."""
from typing import Dict, Optional, TypeVar
from pydantic import BaseModel

from .state_types import SessionState, ActionState, FSAgentState

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
            is_finished=False
        ),
        action=ActionState(
            planned_action=None,
            action_result=None,
            action_counter={}
        )
    )