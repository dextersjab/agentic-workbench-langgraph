"""Support Desk workflow state management."""
from typing import List, Dict, Any, Optional, Type, TypeVar
from typing_extensions import TypedDict
from pydantic import BaseModel

from src.workflows.support_desk.constants import MAX_GATHERING_ROUNDS, IssueCategoryType, IssuePriorityType

T = TypeVar('T', bound=BaseModel)


class SupportDeskState(TypedDict):
    """
    State for the Support Desk IT support workflow.
    
    This state tracks the conversation and context needed for IT support ticket processing.
    """
    # Core conversation data
    messages: List[Dict[str, str]]  # Chat messages in OpenAI format
    current_user_input: str         # Latest user message
    
    # Workflow tracking  
    needs_clarification: bool       # Whether more info is needed (set by clarify_check)
    clarification_attempts: int     # Number of questions asked
    max_clarification_attempts: int # Limit on questions
    
    # Issue information (populated during workflow)
    issue_category: Optional[IssueCategoryType]   # hardware, software, access, network, other
    issue_priority: Optional[IssuePriorityType]   # P1, P2, P3
    
    # Information gathering tracking
    gathering_round: int            # Current round of info gathering
    max_gathering_rounds: int       # Maximum rounds allowed
    needs_more_info: bool          # Whether more info is needed
    info_completeness_confidence: Optional[float]  # Confidence in completeness
    missing_categories: List[str]   # Categories still missing info
    
    # User context
    user_context: Dict[str, Any]    # User info (role, department, etc.)
    
    # Response data
    current_response: str           # Response being built
    custom_llm_chunk: Optional[str] # For streaming
    
    # Ticket generation and final details
    ticket_id: Optional[str]        # Generated ticket ID
    ticket_status: Optional[str]    # Status of the ticket
    assigned_team: Optional[str]    # Final assigned team
    sla_commitment: Optional[str]   # Service level agreement
    next_steps: Optional[str]       # What happens next
    contact_information: Dict[str, str]  # Support contact details
    estimated_resolution_time: Optional[str]  # Expected resolution time
    escalation_path: Optional[str]  # Escalation procedure


def create_initial_state() -> SupportDeskState:
    """
    Create initial state for Support Desk workflow.
    
    Returns:
        A new SupportDeskState with default values.
    """
    return SupportDeskState(
        messages=[],
        current_user_input="",
        needs_clarification=False,
        clarification_attempts=0,
        max_clarification_attempts=3,
        issue_category=None,
        issue_priority=None,
        gathering_round=1,
        max_gathering_rounds=MAX_GATHERING_ROUNDS,
        needs_more_info=True,
        info_completeness_confidence=None,
        missing_categories=[],
        user_context={},
        current_response="",
        custom_llm_chunk=None,
        ticket_id=None,
        ticket_status=None,
        assigned_team=None,
        sla_commitment=None,
        next_steps=None,
        contact_information={},
        estimated_resolution_time=None,
        escalation_path=None
    )


def update_state_from_output(state: SupportDeskState, output: T, 
                           field_mapping: Optional[Dict[str, str]] = None) -> None:
    """
    Update state fields from a Pydantic model output with type safety.
    
    Args:
        state: The workflow state to update
        output: Pydantic model with output data
        field_mapping: Optional mapping of {output_field: state_field}
                      Defaults to direct field name mapping
    
    Example:
        update_state_from_output(state, clarify_output, {
            'needs_clarification': 'needs_clarification',
            'response': 'current_response'
        })
    """
    if field_mapping is None:
        # Try direct field mapping by default
        field_mapping = {}
        output_fields = set(output.model_fields.keys())
        state_fields = set(state.keys())
        
        # Map fields that exist in both
        for field in output_fields:
            if field in state_fields:
                field_mapping[field] = field
    
    # Update state with mapped fields
    for output_field, state_field in field_mapping.items():
        if hasattr(output, output_field) and state_field in state:
            value = getattr(output, output_field)
            state[state_field] = value