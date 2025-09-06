"""Support Desk workflow state management."""

from typing import TypeVar
from pydantic import BaseModel

from src.workflows.support_desk.business_context import MAX_GATHERING_ROUNDS
from .state_types import (
    ClarificationState,
    ClassificationState,
    GatheringState,
    TicketState,
    SupportDeskState,
)

T = TypeVar("T", bound=BaseModel)


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
            issue_category=None, issue_priority=None, assigned_team=None
        ),
        gathering=GatheringState(
            needs_clarification=False,
            clarification_attempts=0,
            max_clarification_attempts=3,
            gathering_round=1,
            max_gathering_rounds=MAX_GATHERING_ROUNDS,
            needs_more_info=True,
            info_completeness_confidence=None,
            missing_categories=[],
        ),
        ticket=TicketState(
            ticket_id=None,
            ticket_status=None,
            sla_commitment=None,
            next_steps=None,
            contact_information={},
            estimated_resolution_time=None,
            escalation_path=None,
        ),
        user_context={},
    )


def update_state_from_output(state: SupportDeskState, output: T) -> None:
    """
    Update state fields from a Pydantic model output.

    This is currently only used by route_issue to set:
    - classification.assigned_team
    - ticket.estimated_resolution_time  
    - ticket.escalation_path

    Args:
        state: The workflow state to update
        output: Pydantic model with output data (RouteOutput)
    """
    # Direct assignment - state structure is always initialized
    if hasattr(output, 'support_team'):
        state["classification"]["assigned_team"] = output.support_team
    
    if hasattr(output, 'estimated_resolution_time'):
        state["ticket"]["estimated_resolution_time"] = output.estimated_resolution_time
    
    if hasattr(output, 'escalation_path'):
        state["ticket"]["escalation_path"] = output.escalation_path
