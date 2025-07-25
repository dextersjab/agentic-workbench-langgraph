# State Management Design for IT Service Desk

## Overview

This document provides a detailed design for the state management component of the IT Service Desk workflow. The state management is responsible for tracking the conversation context, user information, and workflow progress throughout the support desk interaction.

## State Structure

The `SupportDeskState` will be implemented as a TypedDict with the following structure:

```python
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
```

## Initial State Function

The `create_initial_state` function will initialize the state with default values:

```python
def create_initial_state() -> SupportDeskState:
    """
    Create initial state for Support Desk workflow.
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
```

## State Management Considerations

### Conversation History

The `messages` field stores the conversation history in OpenAI format, which includes:
- Role (user/assistant/system)
- Content (the message text)

This allows for context preservation across multiple turns of conversation, which is essential for the clarification loop.

### Clarification Loop State

Three fields manage the clarification loop:
- `needs_clarification`: Boolean flag indicating if more information is needed
- `clarification_attempts`: Counter for how many questions have been asked
- `max_clarification_attempts`: Limit to prevent infinite loops

The conditional edge in the workflow will use `needs_clarification` to determine whether to loop back to the clarification node or proceed to classification.

### Issue Information

As the workflow progresses, these fields will be populated:
- `issue_category`: The type of IT issue (hardware, software, access, other)
- `issue_priority`: The urgency/impact level (high, medium, low)
- `support_team`: The team that will handle the issue
- `ticket_info`: Comprehensive information about the ticket

### User Context

The `user_context` field can store information about the user that might be relevant for handling their issue, such as:
- Department
- Role
- Location
- Previous issues
- System access levels

### Response Management

The `current_response` and `custom_llm_chunk` fields support streaming responses to the user, which provides a more interactive experience.

### Ticket Information

The `ticket_id` and `ticket_status` fields track the generated support ticket, which would be created in a real system but will be simulated in this educational implementation.

## State Transitions

Each node in the workflow will receive the current state, modify it based on its logic, and return the updated state. The key state transitions are:

1. **Clarify Issue Node**:
   - Updates `needs_clarification` based on analysis
   - Increments `clarification_attempts` if asking a question
   - Adds assistant message to `messages`

2. **Classify Issue Node**:
   - Sets `issue_category` based on analysis
   - May update `issue_priority` if determined during classification

3. **Triage Issue Node**:
   - Sets `support_team` based on category and priority
   - May update `ticket_info` with routing information

4. **Gather Info Node**:
   - Populates `ticket_info` with comprehensive details
   - May update `user_context` with additional information

5. **Send to Desk Node**:
   - Generates `ticket_id`
   - Sets `ticket_status` to "created"
   - Formats final response

## Immutability and Deep Copying

To ensure state integrity, each node should create a deep copy of the state before modifying it:

```python
def some_node(state: SupportDeskState) -> SupportDeskState:
    state = deepcopy(state)
    # Modify state...
    return state
```

This prevents unintended side effects and makes debugging easier.

## Error Handling

The state should include provisions for error handling:

1. If a node encounters an error, it should still return a valid state
2. Errors should be logged but not exposed to the user
3. The workflow should be able to continue even if some information is missing

## Educational Considerations

For the educational purpose of this system:

1. The state structure is deliberately simplified compared to a production system
2. Comments explain the purpose of each field for students
3. The state is designed to support both Phase 1 (linear workflow) and Phase 2 (conditional loop)
4. Fields are named intuitively to make the code self-documenting

## Implementation Notes

The state management will be implemented in `src/workflows/support_desk/state.py` and will include:

1. Import statements for required types
2. The `SupportDeskState` TypedDict definition
3. The `create_initial_state` function
4. Any helper functions for state manipulation

This design provides a solid foundation for the workflow while remaining simple enough for educational purposes.