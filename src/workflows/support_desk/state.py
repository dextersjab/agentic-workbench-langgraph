"""Support Desk workflow state management."""
from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict


class SupportDeskState(TypedDict):
    """
    State for the Support Desk IT support workflow.
    
    This state tracks the conversation and context needed for IT support ticket processing.
    """
    # Core conversation data
    messages: List[Dict[str, str]]  # Chat messages in OpenAI format
    current_user_input: str         # Latest user message
    
    # Workflow tracking
    needs_clarification: bool       # Whether more info is needed
    clarification_attempts: int     # Number of questions asked
    max_clarification_attempts: int # Limit on questions
    
    # Issue information (populated during workflow)
    issue_category: Optional[str]   # hardware, software, access, other
    issue_priority: Optional[str]   # high, medium, low
    support_team: Optional[str]     # L1 support, specialist, escalation
    ticket_info: Dict[str, Any]     # Complete ticket information
    
    # User context
    user_context: Dict[str, Any]    # User info (role, department, etc.)
    
    # Response data
    current_response: str           # Response being built
    custom_llm_chunk: Optional[str] # For streaming
    
    # Ticket generation
    ticket_id: Optional[str]        # Generated ticket ID
    ticket_status: Optional[str]    # Status of the ticket


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
        support_team=None,
        ticket_info={},
        user_context={},
        current_response="",
        custom_llm_chunk=None,
        ticket_id=None,
        ticket_status=None
    )