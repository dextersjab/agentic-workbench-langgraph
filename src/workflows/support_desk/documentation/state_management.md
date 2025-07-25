# State Management Design for IT Service Desk

## Overview

This document outlines the state management design for the Support Desk workflow. The state management system is responsible for tracking the conversation state across multiple turns, including user inputs, system responses, and workflow metadata.

## State Structure

The state is implemented as a TypedDict in `src/workflows/support_desk/state.py` with the following structure:

```python
class SupportDeskState(TypedDict):
    """State for the Support Desk workflow."""
    
    # User input
    current_user_input: str
    
    # Conversation history
    messages: List[Dict[str, Any]]
    
    # Issue information
    issue_description: str
    issue_category: Optional[str]
    issue_priority: Optional[str]
    issue_complexity: Optional[str]
    
    # Additional information
    required_info: List[str]
    gathered_info: Dict[str, str]
    
    # Workflow control
    needs_clarification: bool
    is_ready_for_desk: bool
    desk_assignment: Optional[str]
    
    # Metadata
    workflow_step: str
    clarification_count: int
    max_clarification_attempts: int
```

## State Fields

### User Input
- `current_user_input`: The most recent input from the user

### Conversation History
- `messages`: A list of all messages in the conversation, including user and assistant messages

### Issue Information
- `issue_description`: A clear description of the user's issue
- `issue_category`: The category of the issue (e.g., "Hardware", "Software", "Network")
- `issue_priority`: The priority of the issue (e.g., "Low", "Medium", "High", "Critical")
- `issue_complexity`: The complexity of the issue (e.g., "Simple", "Moderate", "Complex")

### Additional Information
- `required_info`: A list of additional information needed to resolve the issue
- `gathered_info`: A dictionary of information gathered from the user

### Workflow Control
- `needs_clarification`: A flag indicating whether the issue needs clarification
- `is_ready_for_desk`: A flag indicating whether the issue is ready to be sent to the service desk
- `desk_assignment`: The service desk to which the issue is assigned

### Metadata
- `workflow_step`: The current step in the workflow
- `clarification_count`: The number of clarification attempts made
- `max_clarification_attempts`: The maximum number of clarification attempts allowed

## Initial State

The initial state is created by the `create_initial_state` function:

```python
def create_initial_state() -> SupportDeskState:
    """Create the initial state for the Support Desk workflow."""
    return {
        # User input
        "current_user_input": "",
        
        # Conversation history
        "messages": [],
        
        # Issue information
        "issue_description": "",
        "issue_category": None,
        "issue_priority": None,
        "issue_complexity": None,
        
        # Additional information
        "required_info": [],
        "gathered_info": {},
        
        # Workflow control
        "needs_clarification": False,
        "is_ready_for_desk": False,
        "desk_assignment": None,
        
        # Metadata
        "workflow_step": "clarify_issue",
        "clarification_count": 0,
        "max_clarification_attempts": 3
    }
```

## State Transitions

The state transitions are managed by the workflow nodes:

1. **clarify_issue**: Updates `issue_description` and `needs_clarification`
2. **classify_issue**: Updates `issue_category`, `issue_priority`, and `issue_complexity`
3. **triage_issue**: Updates `required_info` and `desk_assignment`
4. **gather_info**: Updates `gathered_info` and `is_ready_for_desk`
5. **send_to_desk**: No state updates, just generates the final response

Each node updates the `workflow_step` field to indicate the current step in the workflow.

## Conditional Logic

The workflow uses the following predicates to determine the flow:

1. **needs_clarification_predicate**: Checks if `needs_clarification` is True
2. **is_ready_for_desk_predicate**: Checks if `is_ready_for_desk` is True

These predicates are used to implement the conditional loop logic in the workflow.

## State Usage in Nodes

### clarify_issue Node

The `clarify_issue` node uses the following state fields:
- `current_user_input`: To get the user's input
- `issue_description`: To update with a clear description
- `needs_clarification`: To indicate if clarification is needed
- `clarification_count`: To track the number of clarification attempts
- `max_clarification_attempts`: To limit the number of clarification attempts

### classify_issue Node

The `classify_issue` node uses the following state fields:
- `issue_description`: To classify the issue
- `issue_category`: To update with the issue category
- `issue_priority`: To update with the issue priority
- `issue_complexity`: To update with the issue complexity

### triage_issue Node

The `triage_issue` node uses the following state fields:
- `issue_category`: To determine the appropriate desk
- `issue_priority`: To prioritize the issue
- `issue_complexity`: To determine the required information
- `required_info`: To update with the required information
- `desk_assignment`: To update with the assigned desk

### gather_info Node

The `gather_info` node uses the following state fields:
- `current_user_input`: To get the user's input
- `required_info`: To determine what information to gather
- `gathered_info`: To update with the gathered information
- `is_ready_for_desk`: To indicate if all required information is gathered

### send_to_desk Node

The `send_to_desk` node uses the following state fields:
- `issue_description`: To include in the final response
- `issue_category`: To include in the final response
- `issue_priority`: To include in the final response
- `issue_complexity`: To include in the final response
- `gathered_info`: To include in the final response
- `desk_assignment`: To include in the final response

## Educational Value

This state management design demonstrates several important concepts:

1. **TypedDict**: How to use TypedDict for type-safe state management
2. **State Transitions**: How to manage state transitions in a workflow
3. **Conditional Logic**: How to use state for conditional logic
4. **Immutable State**: How to work with immutable state in a functional workflow

Students will learn:
- How to design a state structure for a workflow
- How to manage state transitions in a workflow
- How to use state for conditional logic
- How to work with immutable state in a functional workflow

## Implementation Notes

The state management is implemented in `src/workflows/support_desk/state.py` and includes:

1. The `SupportDeskState` TypedDict definition
2. The `create_initial_state` function
3. Type hints for all state fields

The state is used by all workflow nodes to manage the conversation state across multiple turns.