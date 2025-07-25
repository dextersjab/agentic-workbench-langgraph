# Support Desk Architecture

## Overview

This document outlines the architecture of the Support Desk workflow, which is designed to replace the existing HelpHub workflow. The Support Desk workflow is an IT service desk implementation that features conditional loop pedagogy, making it an effective educational tool for teaching prompt engineering and LangGraph conditional logic.

## System Architecture

The Support Desk workflow is built using LangGraph, a framework for building stateful, multi-step AI workflows. The architecture consists of the following components:

1. **State Management**: Defines the structure of the conversation state
2. **Workflow Nodes**: Implements the business logic for each step in the workflow
3. **Prompts**: Defines the prompts used by each node to generate responses
4. **Workflow Graph**: Connects the nodes together to form a directed graph
5. **API Integration**: Exposes the workflow through an OpenAI-compatible API
6. **Registry**: Manages the available workflows and provides them to the API

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                        Support Desk Workflow                        │
│                                                                     │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │             │     │             │     │             │           │
│  │ clarify_issue│────▶│classify_issue│────▶│ triage_issue │           │
│  │             │     │             │     │             │           │
│  └─────────────┘     └─────────────┘     └──────┬──────┘           │
│                                                 │                  │
│                                                 ▼                  │
│                                          ┌─────────────┐           │
│                                          │             │           │
│                                          │ gather_info │◀──┐       │
│                                          │             │   │       │
│                                          └──────┬──────┘   │       │
│                                                 │          │       │
│                                                 │          │       │
│                                                 ▼          │       │
│                                          ┌─────────────┐   │       │
│                                          │             │   │       │
│                                          │send_to_desk │   │       │
│                                          │             │   │       │
│                                          └─────────────┘   │       │
│                                                            │       │
│                                                            │       │
│                                          needs_clarification       │
│                                                            │       │
│                                                            └───────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                          Workflow Registry                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                           OpenAI API                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                           Open WebUI                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. State Management

The state management system is implemented in `src/workflows/support_desk/state.py` and defines the structure of the conversation state using a TypedDict:

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

The state is initialized using the `create_initial_state` function:

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

### 2. Workflow Nodes

The workflow nodes are implemented in `src/workflows/support_desk/nodes/` and include:

1. **clarify_issue**: Ensures the user's issue is clearly understood
2. **classify_issue**: Categorizes the issue and assigns priority and complexity
3. **triage_issue**: Determines what additional information is needed and which desk to assign
4. **gather_info**: Collects additional information from the user
5. **send_to_desk**: Generates the final response with the issue details and assignment

Each node is implemented as a function that takes a state and returns an updated state and a response:

```python
def clarify_issue(state: SupportDeskState) -> Tuple[SupportDeskState, str]:
    """Clarify the user's issue."""
    # Implementation details...
    return new_state, response
```

### 3. Prompts

The prompts are implemented in `src/workflows/support_desk/prompts/` and include:

1. **clarify_issue_prompt**: Used by the `clarify_issue` node
2. **classify_issue_prompt**: Used by the `classify_issue` node
3. **triage_issue_prompt**: Used by the `triage_issue` node
4. **gather_info_prompt**: Used by the `gather_info` node
5. **send_to_desk_prompt**: Used by the `send_to_desk` node

Each prompt is implemented as a LangChain prompt template with a system message, user message, and output parser:

```python
clarify_issue_system_message = """
You are an IT Service Desk assistant. Your task is to clarify the user's issue to ensure it is well-understood.
# ... (system message details)
"""

clarify_issue_user_message = """
User input: {user_input}
# ... (user message details)
"""

clarify_issue_prompt = ChatPromptTemplate.from_messages([
    ("system", clarify_issue_system_message),
    ("user", clarify_issue_user_message)
])

clarify_issue_output_parser = StrOutputParser() | JsonOutputParser()
clarify_issue_prompt = clarify_issue_prompt | clarify_issue_output_parser
```

### 4. Workflow Graph

The workflow graph is implemented in `src/workflows/support_desk/workflow.py` and connects the nodes together to form a directed graph:

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

### 5. API Integration

The API integration is implemented in `src/core/api.py` and exposes the workflow through an OpenAI-compatible API:

```python
@v1_router.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """Handle OpenAI-compatible chat completion requests."""
    logger.info(f"Chat completion request - model: {request.model}, stream: {request.stream}")
    
    if request.stream:
        logger.info("Starting streaming response")
        return StreamingResponse(
            _sse_generator(request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*"
            }
        )
    else:
        logger.info("Starting non-streaming response")
        return await _create_non_streaming_response(request)
```

### 6. Registry

The registry is implemented in `src/workflows/registry.py` and manages the available workflows:

```python
class WorkflowRegistry:
    """Registry for managing available workflows."""
    
    _workflows: Dict[str, RunnableSequence] = {}
    _default_workflow: str = "support_desk"
    
    @classmethod
    def register_workflow(cls, name: str, workflow: RunnableSequence) -> None:
        """Register a workflow with the registry."""
        logger.info(f"Registering workflow: {name}")
        cls._workflows[name] = workflow
    
    @classmethod
    def get_workflow(cls, name: str = None) -> RunnableSequence:
        """Get a workflow by name."""
        if name is None:
            name = cls._default_workflow
            logger.info(f"No workflow name provided, using default: {name}")
        
        if name not in cls._workflows:
            logger.error(f"Workflow not found: {name}")
            raise KeyError(f"Workflow not found: {name}")
        
        logger.info(f"Returning workflow: {name}")
        return cls._workflows[name]
```

## Conditional Loop Logic

The key feature of the Support Desk workflow is the conditional loop logic, which allows the workflow to loop back to the `gather_info` node if clarification is needed:

```python
def needs_clarification_predicate(state: SupportDeskState) -> bool:
    """Check if the issue needs clarification."""
    return state["needs_clarification"]

builder.add_conditional_edges(
    "gather_info",
    needs_clarification_predicate,
    {
        True: "gather_info",  # Loop back if clarification is needed
        False: "send_to_desk"  # Proceed if no clarification is needed
    }
)
```

This conditional loop demonstrates an advanced LangGraph pattern and serves as an educational example of how to implement conditional logic in a workflow.

## Educational Value

The Support Desk workflow is designed to be an educational tool for teaching prompt engineering and LangGraph conditional logic. It demonstrates:

1. **LangGraph Fundamentals**: How to create a directed graph of nodes
2. **Conditional Logic**: How to implement conditional paths in a workflow
3. **Prompt Engineering**: How to design effective prompts for different business tasks
4. **State Management**: How to manage state across conversation turns
5. **API Integration**: How to expose a workflow through an API

## Implementation Plan

The implementation of the Support Desk workflow follows this plan:

1. **Design Phase**:
   - Design the state structure
   - Design the node implementations
   - Design the prompts
   - Design the workflow graph
   - Design the API integration
   - Design the registry updates

2. **Implementation Phase**:
   - Implement the state management
   - Implement the node functions
   - Implement the prompts
   - Implement the workflow graph
   - Update the registry
   - Update the API integration

3. **Testing Phase**:
   - Test the workflow with example conversations
   - Verify the conditional loop logic
   - Ensure the API integration works correctly

## Conclusion

The Support Desk workflow is a comprehensive implementation of an IT service desk that features conditional loop pedagogy. It serves as an educational tool for teaching prompt engineering and LangGraph conditional logic, while also providing a practical example of how to build a stateful, multi-step AI workflow.