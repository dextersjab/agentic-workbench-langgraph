# Support Desk Workflow

This directory contains the implementation of the IT Service Desk workflow with conditional loop logic.

## Directory Structure

```
support_desk/
├── workflow.py              # Main workflow definition with conditional logic
├── state.py                 # State management
├── nodes/                   # Node implementations
├── prompts/                 # Prompt templates
└── examples/                # Example conversations
```

## Workflow Overview

The Support Desk workflow implements an IT service desk agent that:

1. Clarifies user issues when needed (with conditional loop)
2. Classifies issues into categories
3. Triages issues to appropriate support teams
4. Gathers additional information
5. Creates support tickets

## Key Components

### [workflow.py](workflow.py)

Defines the LangGraph workflow with conditional loop logic. The key feature is the conditional edge from the `clarify_issue` node that can either loop back to itself or proceed to the `classify_issue` node based on the state.

```python
# Conditional edge example
workflow.add_conditional_edges(
    "clarify_issue",
    should_continue_clarifying,
    {
        "clarify": "clarify_issue",  # Loop back to clarify
        "classify": "classify_issue"  # Proceed to classification
    }
)
```

### [state.py](state.py)

Defines the `SupportDeskState` TypedDict that tracks conversation context, user information, and workflow progress.

### [nodes/](nodes/)

Contains the implementation of each node in the workflow:
- `clarify_issue.py`: Analyzes user input and asks clarifying questions
- `classify_issue.py`: Categorizes issues into predefined types
- `triage_issue.py`: Routes issues to appropriate support teams
- `gather_info.py`: Collects additional information
- `send_to_desk.py`: Creates tickets and formats responses

### [prompts/](prompts/)

Contains prompt templates for each node, demonstrating effective prompt engineering techniques.

### [examples/](examples/)

Contains example conversations showing the workflow in action with different types of user inputs.

## Usage

The workflow is registered in the `WorkflowRegistry` and can be accessed through the API:

```python
workflow = WorkflowRegistry.get_workflow("support_desk")
```

## Learning Focus

This workflow demonstrates two key educational concepts:

1. **Prompt Engineering**: Each node uses carefully designed prompts
2. **Conditional Logic in LangGraph**: The clarification loop shows how to implement conditional edges