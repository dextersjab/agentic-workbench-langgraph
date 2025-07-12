"""HelpHub workflow state management."""
from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict


class HelpHubState(TypedDict):
    """
    State for the HelpHub IT support workflow.
    
    This state tracks the conversation and context needed for IT support ticket processing.
    """
    # Core conversation data
    messages: List[Dict[str, str]]  # Chat messages in OpenAI format
    current_user_input: str         # Latest user message
    
    # Knowledge base context
    kb_articles: List[Dict[str, Any]]  # Relevant KB articles loaded as context
    
    # User context
    user_context: Dict[str, Any]    # User info (role, department, urgency, etc.)
    
    # Workflow tracking
    needs_clarification: bool       # Whether more info is needed
    clarification_attempts: int     # Number of questions asked
    max_clarification_attempts: int # Limit on questions
    
    # Ticket information (populated during workflow)
    ticket_category: Optional[str]  # hardware/software/network/access/billing
    ticket_priority: Optional[str]  # P1/P2/P3
    ticket_queue: Optional[str]     # L1-Hardware, L2-Software, etc.
    ticket_id: Optional[str]        # Generated ticket ID
    
    # Multi-issue handling
    additional_issues: List[str]    # Secondary issues to handle later
    
    # ServiceHub integration
    servicehub_response: Optional[Dict[str, Any]]  # Response from ticket creation
    
    # Streaming/response data
    current_response: str           # Response being built
    custom_llm_chunk: Optional[str] # For streaming to Open WebUI


def create_initial_state() -> HelpHubState:
    """
    Create initial state for HelpHub workflow.
    
    TODO for participants: Consider what additional fields might be needed
    for tracking conversation context or user preferences.
    """
    return HelpHubState(
        messages=[],
        current_user_input="",
        kb_articles=[],
        user_context={},
        needs_clarification=False,
        clarification_attempts=0,
        max_clarification_attempts=3,
        ticket_category=None,
        ticket_priority=None,
        ticket_queue=None,
        ticket_id=None,
        additional_issues=[],
        servicehub_response=None,
        current_response="",
        custom_llm_chunk=None
    )