"""Composed state type definitions for Support Desk workflow using TypedDict."""

from typing import List, Dict, Any, Literal, Optional
from typing_extensions import TypedDict

from .business_context import IssueCategoryType, IssuePriorityType


class ClassificationState(TypedDict):
    """State related to issue classification and assignment."""

    issue_category: Optional[
        IssueCategoryType
    ]  # hardware, software, access, network, other
    issue_priority: Optional[IssuePriorityType]  # P1, P2, P3, P4
    assigned_team: Optional[str]  # Final assigned team


class ClarificationState(TypedDict):
    """State related to clarifying category and priority classifications"""

    # awaiting_reply: bool            # determines whether we're waiting for the HITL or responding
    status: Literal["satisfied", "capped", "escalated", "awaiting_user"]
    clarification_attempts: int  # tracks number of times HITL has been called
    max_clarification_attempts: (
        int  # determines maximum number of HITL calls for this node
    )


class GatheringState(TypedDict):
    """State related to information gathering process."""

    needs_clarification: bool  # Whether more info is needed (set by clarify_check)
    clarification_attempts: int  # Number of questions asked
    max_clarification_attempts: int  # Limit on questions
    gathering_round: int  # Current round of info gathering
    max_gathering_rounds: int  # Maximum rounds allowed
    needs_more_info: bool  # Whether more info is needed
    info_completeness_confidence: Optional[float]  # Confidence in completeness
    missing_categories: List[str]  # Categories still missing info


class TicketState(TypedDict):
    """State related to ticket generation and support details."""

    ticket_id: Optional[str]  # Generated ticket ID
    ticket_status: Optional[str]  # Status of the ticket
    sla_commitment: Optional[str]  # Service level agreement
    next_steps: Optional[str]  # What happens next
    contact_information: Dict[str, str]  # Support contact details
    estimated_resolution_time: Optional[str]  # Expected resolution time
    escalation_path: Optional[str]  # Escalation procedure


class SupportDeskState(TypedDict):
    """
    Composed state for the Support Desk IT support workflow.

    This state uses composition to group related fields for better organization.
    """

    messages: List[Dict[str, str]]  # Chat messages in OpenAI format
    classification: ClassificationState
    clarification: ClarificationState
    gathering: GatheringState
    ticket: TicketState
    user_context: Dict[str, Any]  # User info (role, department, etc.)
