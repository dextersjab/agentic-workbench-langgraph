# Learning Outcomes for IT Service Desk

## Overview

This document outlines the learning outcomes for the Support Desk workflow. The workflow is designed to be an educational tool for teaching prompt engineering and LangGraph conditional logic. It provides a practical example of how to build a stateful, multi-step AI workflow with conditional paths.

## Learning Progression

The Support Desk workflow is designed to support a two-phase learning progression:

1. **Linear Workflow**: Understanding the basics of LangGraph and prompt engineering
2. **Conditional Loop**: Advanced concepts including conditional logic and state management

## Key Learning Outcomes

### 1. LangGraph Fundamentals

Students will learn:

- **Graph Construction**: How to create a directed graph of nodes using LangGraph's `StateGraph`
- **Node Implementation**: How to implement node functions that process state and return responses
- **Edge Definition**: How to define edges between nodes to create a workflow
- **State Management**: How to define and manage state using TypedDict
- **Workflow Compilation**: How to compile a workflow and make it executable

```python
# Example of graph construction
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
```

### 2. Conditional Logic

Students will learn:

- **Predicate Functions**: How to implement functions that examine state to determine workflow paths
- **Conditional Edges**: How to add conditional edges to a workflow based on predicate functions
- **Branching Logic**: How to create branches in a workflow based on conditions
- **Looping Constructs**: How to implement loops in a workflow for iterative processing

```python
# Example of predicate function
def needs_clarification_predicate(state: SupportDeskState) -> bool:
    """Check if the issue needs clarification."""
    return state["needs_clarification"]

# Example of conditional edge
builder.add_conditional_edges(
    "gather_info",
    needs_clarification_predicate,
    {
        True: "gather_info",  # Loop back if clarification is needed
        False: "send_to_desk"  # Proceed if no clarification is needed
    }
)
```

### 3. Prompt Engineering

Students will learn:

- **System Messages**: How to design effective system messages that provide context and instructions
- **User Messages**: How to format user messages with dynamic content
- **Output Parsing**: How to extract structured information from model responses
- **Prompt Templates**: How to create reusable prompt templates with LangChain
- **Chain of Thought**: How to guide the model's reasoning process through prompt design

```python
# Example of prompt template
clarify_issue_system_message = """
You are an IT Service Desk assistant. Your task is to clarify the user's issue to ensure it is well-understood.

Given the user's input, you should:
1. Determine if the issue is clear and specific enough to proceed
2. If the issue is unclear, ask for clarification
3. If the issue is clear, summarize it in a concise description

Your response should include:
- A clear description of the issue (as you understand it)
- Whether clarification is needed
- A response to the user (either confirming the issue or asking for clarification)
"""

clarify_issue_user_message = """
User input: {user_input}

Clarification count: {clarification_count}
Maximum clarification attempts: {max_clarification_attempts}
"""

clarify_issue_prompt = ChatPromptTemplate.from_messages([
    ("system", clarify_issue_system_message),
    ("user", clarify_issue_user_message)
])
```

### 4. State Management

Students will learn:

- **TypedDict**: How to use TypedDict for type-safe state management
- **State Transitions**: How to manage state transitions in a workflow
- **Immutable State**: How to work with immutable state in a functional workflow
- **State Initialization**: How to initialize state for a workflow
- **State Access**: How to access and update state in node functions

```python
# Example of state definition
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

### 5. API Integration

Students will learn:

- **FastAPI**: How to create an API with FastAPI
- **OpenAI Compatibility**: How to create an OpenAI-compatible API
- **Streaming Responses**: How to implement streaming responses with SSE
- **Error Handling**: How to handle errors in an API context
- **Middleware**: How to use middleware for CORS and other functionality

```python
# Example of API endpoint
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

### 6. Workflow Registry

Students will learn:

- **Dependency Injection**: How to use a registry to manage dependencies
- **Factory Pattern**: How to use factory functions to create workflows
- **Singleton Pattern**: How to use a singleton registry to manage workflows
- **Configuration Management**: How to configure the application to use different workflows

```python
# Example of workflow registry
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

## Educational Exercises

The Support Desk workflow can be used for various educational exercises:

### 1. Linear Workflow Exercise

Students implement a simple linear workflow with the following nodes:
- `clarify_issue`
- `classify_issue`
- `triage_issue`
- `send_to_desk`

This exercise focuses on the basics of LangGraph and prompt engineering.

### 2. Conditional Loop Exercise

Students extend the linear workflow to include a conditional loop:
- Add the `gather_info` node
- Implement the `needs_clarification_predicate` function
- Add conditional edges to create a loop

This exercise focuses on conditional logic and state management.

### 3. Prompt Engineering Exercise

Students design and implement prompts for each node:
- Design system messages
- Format user messages
- Implement output parsing

This exercise focuses on prompt engineering techniques.

### 4. State Management Exercise

Students design and implement the state management system:
- Define the `SupportDeskState` TypedDict
- Implement the `create_initial_state` function
- Update state in node functions

This exercise focuses on state management techniques.

### 5. API Integration Exercise

Students integrate the workflow with the API:
- Implement the chat completions endpoint
- Add streaming support
- Handle errors

This exercise focuses on API integration techniques.

## Implementation Notes

The Support Desk workflow is implemented in a modular way to support these learning outcomes:

1. **State Management**: Implemented in `src/workflows/support_desk/state.py`
2. **Node Functions**: Implemented in `src/workflows/support_desk/nodes/`
3. **Prompts**: Implemented in `src/workflows/support_desk/prompts/`
4. **Workflow**: Implemented in `src/workflows/support_desk/workflow.py`
5. **Registry**: Implemented in `src/workflows/registry.py`
6. **API**: Implemented in `src/core/api.py`

Each component is designed to be modular and reusable, allowing for easy modification and extension for educational purposes.

## Conclusion

The Support Desk workflow provides a comprehensive educational tool for teaching prompt engineering and LangGraph conditional logic. It demonstrates key concepts in a practical, real-world context, allowing students to learn by example and through hands-on exercises.