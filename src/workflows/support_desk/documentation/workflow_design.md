# Workflow Design for IT Service Desk

## Overview

This document outlines the workflow design for the Support Desk system. The workflow is implemented using LangGraph, a framework for building stateful, multi-step AI workflows. The workflow is designed to demonstrate conditional loop logic, which is a key concept in LangGraph.

## Workflow Structure

The workflow is implemented in `src/workflows/support_desk/workflow.py` and consists of the following nodes:

1. **clarify_issue**: Ensures the user's issue is clearly understood
2. **classify_issue**: Categorizes the issue and assigns priority and complexity
3. **triage_issue**: Determines what additional information is needed and which desk to assign
4. **gather_info**: Collects additional information from the user
5. **send_to_desk**: Generates the final response with the issue details and assignment

## Workflow Diagram

```
                    ┌───────────────┐
                    │ clarify_issue │
                    └───────┬───────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │                         │
              │                         │
              ▼                         │
┌───────────────────────┐    needs_clarification
│    classify_issue     │               │
└───────────┬───────────┘               │
            │                           │
            │                           │
            ▼                           │
┌───────────────────────┐               │
│     triage_issue      │               │
└───────────┬───────────┘               │
            │                           │
            │                           │
            ▼                           │
┌───────────────────────┐               │
│     gather_info       │◄──────────────┘
└───────────┬───────────┘
            │
            │  is_ready_for_desk
            ▼
┌───────────────────────┐
│     send_to_desk      │
└───────────────────────┘
```

## Conditional Logic

The workflow includes two conditional paths:

1. **Clarification Loop**: If the issue needs clarification, the workflow loops back to the `gather_info` node
2. **Ready for Desk**: If all required information is gathered, the workflow proceeds to the `send_to_desk` node

These conditional paths are implemented using predicate functions:

```python
def needs_clarification_predicate(state: SupportDeskState) -> bool:
    """Check if the issue needs clarification."""
    return state["needs_clarification"]

def is_ready_for_desk_predicate(state: SupportDeskState) -> bool:
    """Check if the issue is ready to be sent to the service desk."""
    return state["is_ready_for_desk"]
```

## Workflow Implementation

The workflow is created using the `create_support_desk_workflow` function:

```python
def create_support_desk_workflow() -> Graph:
    """Create the Support Desk workflow."""
    # Create the workflow builder
    builder = StateGraph(SupportDeskState)
    
    # Add nodes to the workflow
    builder.add_node("clarify_issue", clarify_issue)
    builder.add_node("classify_issue", classify_issue)
    builder.add_node("triage_issue", triage_issue)
    builder.add_node("gather_info", gather_info)
    builder.add_node("send_to_desk", send_to_desk)
    
    # Define the workflow edges
    builder.add_edge("clarify_issue", "classify_issue")
    builder.add_edge("classify_issue", "triage_issue")
    builder.add_edge("triage_issue", "gather_info")
    
    # Add conditional edges
    builder.add_conditional_edges(
        "gather_info",
        needs_clarification_predicate,
        {
            True: "gather_info",  # Loop back if clarification is needed
            False: "send_to_desk"  # Proceed if no clarification is needed
        }
    )
    
    # Set the entry point
    builder.set_entry_point("clarify_issue")
    
    # Compile the workflow
    workflow = builder.compile()
    
    return workflow
```

## Node Functions

Each node in the workflow is implemented as a function that takes a state and returns an updated state and a response:

### clarify_issue

```python
def clarify_issue(state: SupportDeskState) -> Tuple[SupportDeskState, str]:
    """Clarify the user's issue."""
    # Get the user input
    user_input = state["current_user_input"]
    
    # Use the clarify_issue prompt to generate a response
    response = clarify_issue_prompt.invoke({
        "user_input": user_input,
        "clarification_count": state["clarification_count"],
        "max_clarification_attempts": state["max_clarification_attempts"]
    })
    
    # Parse the response to get the issue description and whether clarification is needed
    issue_description = response["issue_description"]
    needs_clarification = response["needs_clarification"]
    
    # Update the state
    new_state = state.copy()
    new_state["issue_description"] = issue_description
    new_state["needs_clarification"] = needs_clarification
    new_state["workflow_step"] = "clarify_issue"
    
    if needs_clarification:
        new_state["clarification_count"] += 1
    
    return new_state, response["response"]
```

### classify_issue

```python
def classify_issue(state: SupportDeskState) -> Tuple[SupportDeskState, str]:
    """Classify the user's issue."""
    # Get the issue description
    issue_description = state["issue_description"]
    
    # Use the classify_issue prompt to generate a response
    response = classify_issue_prompt.invoke({
        "issue_description": issue_description
    })
    
    # Parse the response to get the issue category, priority, and complexity
    issue_category = response["issue_category"]
    issue_priority = response["issue_priority"]
    issue_complexity = response["issue_complexity"]
    
    # Update the state
    new_state = state.copy()
    new_state["issue_category"] = issue_category
    new_state["issue_priority"] = issue_priority
    new_state["issue_complexity"] = issue_complexity
    new_state["workflow_step"] = "classify_issue"
    
    return new_state, response["response"]
```

### triage_issue

```python
def triage_issue(state: SupportDeskState) -> Tuple[SupportDeskState, str]:
    """Triage the user's issue."""
    # Get the issue category, priority, and complexity
    issue_category = state["issue_category"]
    issue_priority = state["issue_priority"]
    issue_complexity = state["issue_complexity"]
    
    # Use the triage_issue prompt to generate a response
    response = triage_issue_prompt.invoke({
        "issue_category": issue_category,
        "issue_priority": issue_priority,
        "issue_complexity": issue_complexity
    })
    
    # Parse the response to get the required information and desk assignment
    required_info = response["required_info"]
    desk_assignment = response["desk_assignment"]
    
    # Update the state
    new_state = state.copy()
    new_state["required_info"] = required_info
    new_state["desk_assignment"] = desk_assignment
    new_state["workflow_step"] = "triage_issue"
    
    return new_state, response["response"]
```

### gather_info

```python
def gather_info(state: SupportDeskState) -> Tuple[SupportDeskState, str]:
    """Gather additional information from the user."""
    # Get the user input and required information
    user_input = state["current_user_input"]
    required_info = state["required_info"]
    gathered_info = state["gathered_info"]
    
    # Use the gather_info prompt to generate a response
    response = gather_info_prompt.invoke({
        "user_input": user_input,
        "required_info": required_info,
        "gathered_info": gathered_info,
        "needs_clarification": state["needs_clarification"]
    })
    
    # Parse the response to get the updated gathered information and whether all information is gathered
    updated_gathered_info = response["gathered_info"]
    is_ready_for_desk = response["is_ready_for_desk"]
    needs_clarification = response["needs_clarification"]
    
    # Update the state
    new_state = state.copy()
    new_state["gathered_info"] = updated_gathered_info
    new_state["is_ready_for_desk"] = is_ready_for_desk
    new_state["needs_clarification"] = needs_clarification
    new_state["workflow_step"] = "gather_info"
    
    return new_state, response["response"]
```

### send_to_desk

```python
def send_to_desk(state: SupportDeskState) -> Tuple[SupportDeskState, str]:
    """Send the issue to the service desk."""
    # Get the issue details
    issue_description = state["issue_description"]
    issue_category = state["issue_category"]
    issue_priority = state["issue_priority"]
    issue_complexity = state["issue_complexity"]
    gathered_info = state["gathered_info"]
    desk_assignment = state["desk_assignment"]
    
    # Use the send_to_desk prompt to generate a response
    response = send_to_desk_prompt.invoke({
        "issue_description": issue_description,
        "issue_category": issue_category,
        "issue_priority": issue_priority,
        "issue_complexity": issue_complexity,
        "gathered_info": gathered_info,
        "desk_assignment": desk_assignment
    })
    
    # Update the state
    new_state = state.copy()
    new_state["workflow_step"] = "send_to_desk"
    
    return new_state, response["response"]
```

## Streaming Support

The workflow supports streaming responses using the `custom_llm_chunk` field:

```python
def create_support_desk_workflow() -> Graph:
    """Create the Support Desk workflow."""
    # ... (previous code)
    
    # Configure the workflow for streaming
    workflow = workflow.with_config(
        {
            "recursion_limit": 25,
            "stream_mode": "custom",
            "custom_llm_chunk_key": "custom_llm_chunk"
        }
    )
    
    return workflow
```

This allows the API to stream responses from the workflow to the client.

## Educational Value

This workflow design demonstrates several important concepts:

1. **LangGraph**: How to use LangGraph to build stateful, multi-step AI workflows
2. **Conditional Logic**: How to implement conditional logic in a workflow
3. **Predicate Functions**: How to use predicate functions to determine workflow paths
4. **State Management**: How to manage state across conversation turns
5. **Streaming**: How to support streaming responses

Students will learn:
- How to design a workflow with conditional logic
- How to implement predicate functions
- How to manage state in a workflow
- How to support streaming responses

## Implementation Notes

The workflow is implemented in `src/workflows/support_desk/workflow.py` and includes:

1. The `create_support_desk_workflow` function
2. The predicate functions
3. The node functions
4. Streaming configuration

The workflow is designed to be modular and extensible, allowing for easy modification and extension.