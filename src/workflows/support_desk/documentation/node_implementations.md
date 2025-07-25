# Node Implementations Design for IT Service Desk

## Overview

This document outlines the design of the node implementations for the Support Desk workflow. Each node is responsible for a specific step in the workflow and is implemented as a function that takes a state and returns an updated state and a response.

## Node Structure

Each node follows a similar structure:

1. Extract relevant information from the state
2. Invoke a prompt with the extracted information
3. Parse the response from the prompt
4. Update the state with the parsed information
5. Return the updated state and the response

## Node Implementations

### 1. clarify_issue

The `clarify_issue` node is responsible for ensuring that the user's issue is clearly understood. It uses the `clarify_issue_prompt` to generate a response that either confirms the issue or asks for clarification.

```python
def clarify_issue(state: SupportDeskState) -> Tuple[SupportDeskState, str]:
    """Clarify the user's issue.
    
    This node is responsible for ensuring that the user's issue is clearly understood.
    It uses the clarify_issue_prompt to generate a response that either confirms
    the issue or asks for clarification.
    
    Args:
        state: The current state of the workflow
        
    Returns:
        A tuple containing the updated state and the response to the user
    """
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

#### State Updates

- `issue_description`: Updated with a clear description of the issue
- `needs_clarification`: Set to True if clarification is needed, False otherwise
- `workflow_step`: Set to "clarify_issue"
- `clarification_count`: Incremented if clarification is needed

### 2. classify_issue

The `classify_issue` node is responsible for categorizing the issue and assigning priority and complexity. It uses the `classify_issue_prompt` to generate a response that includes the issue category, priority, and complexity.

```python
def classify_issue(state: SupportDeskState) -> Tuple[SupportDeskState, str]:
    """Classify the user's issue.
    
    This node is responsible for categorizing the issue and assigning priority and complexity.
    It uses the classify_issue_prompt to generate a response that includes the issue category,
    priority, and complexity.
    
    Args:
        state: The current state of the workflow
        
    Returns:
        A tuple containing the updated state and the response to the user
    """
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

#### State Updates

- `issue_category`: Set to the category of the issue (e.g., "Hardware", "Software", "Network")
- `issue_priority`: Set to the priority of the issue (e.g., "Low", "Medium", "High", "Critical")
- `issue_complexity`: Set to the complexity of the issue (e.g., "Simple", "Moderate", "Complex")
- `workflow_step`: Set to "classify_issue"

### 3. triage_issue

The `triage_issue` node is responsible for determining what additional information is needed and which desk to assign the issue to. It uses the `triage_issue_prompt` to generate a response that includes the required information and desk assignment.

```python
def triage_issue(state: SupportDeskState) -> Tuple[SupportDeskState, str]:
    """Triage the user's issue.
    
    This node is responsible for determining what additional information is needed
    and which desk to assign the issue to. It uses the triage_issue_prompt to generate
    a response that includes the required information and desk assignment.
    
    Args:
        state: The current state of the workflow
        
    Returns:
        A tuple containing the updated state and the response to the user
    """
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

#### State Updates

- `required_info`: Set to a list of additional information needed to resolve the issue
- `desk_assignment`: Set to the service desk to which the issue is assigned
- `workflow_step`: Set to "triage_issue"

### 4. gather_info

The `gather_info` node is responsible for collecting additional information from the user. It uses the `gather_info_prompt` to generate a response that either asks for more information or confirms that all required information has been gathered.

```python
def gather_info(state: SupportDeskState) -> Tuple[SupportDeskState, str]:
    """Gather additional information from the user.
    
    This node is responsible for collecting additional information from the user.
    It uses the gather_info_prompt to generate a response that either asks for more
    information or confirms that all required information has been gathered.
    
    Args:
        state: The current state of the workflow
        
    Returns:
        A tuple containing the updated state and the response to the user
    """
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

#### State Updates

- `gathered_info`: Updated with the information gathered from the user
- `is_ready_for_desk`: Set to True if all required information has been gathered, False otherwise
- `needs_clarification`: Set to True if clarification is needed, False otherwise
- `workflow_step`: Set to "gather_info"

### 5. send_to_desk

The `send_to_desk` node is responsible for generating the final response with the issue details and assignment. It uses the `send_to_desk_prompt` to generate a response that includes all the information gathered during the conversation.

```python
def send_to_desk(state: SupportDeskState) -> Tuple[SupportDeskState, str]:
    """Send the issue to the service desk.
    
    This node is responsible for generating the final response with the issue details
    and assignment. It uses the send_to_desk_prompt to generate a response that includes
    all the information gathered during the conversation.
    
    Args:
        state: The current state of the workflow
        
    Returns:
        A tuple containing the updated state and the response to the user
    """
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

#### State Updates

- `workflow_step`: Set to "send_to_desk"

## Predicate Functions

In addition to the node functions, the workflow includes two predicate functions that are used to determine the flow of the conversation:

### 1. needs_clarification_predicate

The `needs_clarification_predicate` function checks if the issue needs clarification:

```python
def needs_clarification_predicate(state: SupportDeskState) -> bool:
    """Check if the issue needs clarification.
    
    This predicate function is used to determine whether the workflow should loop
    back to the gather_info node for clarification.
    
    Args:
        state: The current state of the workflow
        
    Returns:
        True if the issue needs clarification, False otherwise
    """
    return state["needs_clarification"]
```

### 2. is_ready_for_desk_predicate

The `is_ready_for_desk_predicate` function checks if the issue is ready to be sent to the service desk:

```python
def is_ready_for_desk_predicate(state: SupportDeskState) -> bool:
    """Check if the issue is ready to be sent to the service desk.
    
    This predicate function is used to determine whether the workflow should proceed
    to the send_to_desk node.
    
    Args:
        state: The current state of the workflow
        
    Returns:
        True if the issue is ready to be sent to the service desk, False otherwise
    """
    return state["is_ready_for_desk"]
```

## Educational Value

This node implementation design demonstrates several important concepts:

1. **Functional Programming**: How to use pure functions for workflow nodes
2. **State Management**: How to manage state transitions in a workflow
3. **Prompt Engineering**: How to design prompts for different business tasks
4. **Predicate Functions**: How to use predicate functions for conditional logic

Students will learn:
- How to implement workflow nodes as pure functions
- How to manage state transitions in a workflow
- How to design prompts for different business tasks
- How to use predicate functions for conditional logic

## Implementation Notes

The node implementations are located in `src/workflows/support_desk/nodes/` and include:

1. `clarify_issue.py`: Implementation of the `clarify_issue` node
2. `classify_issue.py`: Implementation of the `classify_issue` node
3. `triage_issue.py`: Implementation of the `triage_issue` node
4. `gather_info.py`: Implementation of the `gather_info` node
5. `send_to_desk.py`: Implementation of the `send_to_desk` node
6. `predicates.py`: Implementation of the predicate functions

Each node is designed to be modular and reusable, allowing for easy modification and extension of the workflow.