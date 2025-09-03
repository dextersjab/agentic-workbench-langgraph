"""Support Desk workflow state management."""
from typing import Dict, Optional, TypeVar
from pydantic import BaseModel

from src.workflows.support_desk.business_context import MAX_GATHERING_ROUNDS
from .state_types import ClarificationState, ClassificationState, GatheringState, TicketState, SupportDeskState

T = TypeVar('T', bound=BaseModel)


def create_initial_state() -> SupportDeskState:
    """
    Create initial composed state for Support Desk workflow.
    
    Returns:
        A new SupportDeskState with default values using composition.
    """
    return SupportDeskState(
        messages=[],
        clarification=ClarificationState(
            awaiting_reply=False,
            clarification_attempts=0,
            max_clarification_attempts=MAX_GATHERING_ROUNDS,
        ),
        classification=ClassificationState(
            issue_category=None,
            issue_priority=None,
            assigned_team=None
        ),
        gathering=GatheringState(
            needs_clarification=False,
            clarification_attempts=0,
            max_clarification_attempts=3,
            gathering_round=1,
            max_gathering_rounds=MAX_GATHERING_ROUNDS,
            needs_more_info=True,
            info_completeness_confidence=None,
            missing_categories=[]
        ),
        ticket=TicketState(
            ticket_id=None,
            ticket_status=None,
            sla_commitment=None,
            next_steps=None,
            contact_information={},
            estimated_resolution_time=None,
            escalation_path=None
        ),
        user_context={}
    )


def update_state_from_output(state: SupportDeskState, output: T, 
                           field_mapping: Optional[Dict[str, str]] = None) -> None:
    """
    Update state fields from a Pydantic model output with type safety.
    
    Note: This function needs to be updated to work with the composed state structure.
    For now, it's kept for compatibility but may need revision.
    
    Args:
        state: The workflow state to update
        output: Pydantic model with output data
        field_mapping: Optional mapping of {output_field: state_field}
    """
    # This function will need to be updated to handle the composed structure
    # For now, we'll leave it as a placeholder
    pass