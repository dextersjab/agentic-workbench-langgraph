# Node Implementations Design for IT Service Desk

## Overview

This document provides detailed designs for the five nodes in the IT Service Desk workflow:

1. **clarify_issue**: Analyzes user input and asks clarifying questions when needed
2. **classify_issue**: Categorizes the IT issue into predefined categories
3. **triage_issue**: Routes the issue to the appropriate support team
4. **gather_info**: Collects additional information needed for the support team
5. **send_to_desk**: Formats the final response with ticket information

Each node will be implemented as an async function that takes a `SupportDeskState` as input and returns an updated `SupportDeskState`.

## 1. clarify_issue Node

### Purpose
Analyze user input and generate clarifying questions when needed. This node implements the conditional loop logic that is central to Phase 2 of the learning progression.

### Implementation

```python
async def clarify_issue_node(state: SupportDeskState) -> SupportDeskState:
    """
    Analyze user input and ask clarifying questions if needed.
    
    This node:
    1. Analyzes the user's input for clarity and completeness
    2. Determines if enough information exists to categorize the issue  
    3. Generates clarifying questions if needed
    4. Updates the conversation state appropriately
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with clarification decision and any questions
    """
    
    state = deepcopy(state)
    
    user_input = state.get("current_user_input", "")
    messages = state.get("messages", [])
    clarification_attempts = state.get("clarification_attempts", 0)
    max_attempts = state.get("max_clarification_attempts", 3)
    
    # Build conversation history for context
    conversation_history = "\n".join([
        f"{msg.get('role', 'user')}: {msg.get('content', '')}" 
        for msg in messages[-5:]  # Last 5 messages for context
    ])
    
    try:
        # Step 1: Analyze if input needs clarification using LLM
        analysis_prompt = ANALYSIS_PROMPT.format(
            user_input=user_input,
            conversation_history=conversation_history
        )
        
        # Call LLM to analyze if clarification is needed
        analysis_response = await client.chat_completion(
            messages=[
                {"role": "system", "content": analysis_prompt}
            ],
            model="openai/gpt-4.1-mini",
            temperature=0.3
        )
        
        # Parse the analysis response to determine if clarification is needed
        analysis_content = analysis_response.get("content", "").lower()
        needs_clarification = (
            "needs clarification" in analysis_content or
            "clarification needed" in analysis_content or
            "more information" in analysis_content
        ) and clarification_attempts < max_attempts
        
        # Get stream writer for custom streaming
        writer = get_stream_writer()
        
        if needs_clarification:
            # Generate clarifying question using LLM
            clarification_prompt = CLARIFICATION_PROMPT.format(
                user_input=user_input,
                conversation_history=conversation_history,
                attempt_number=clarification_attempts + 1,
                max_attempts=max_attempts
            )
            
            # Stream callback to emit chunks as they come in
            def stream_callback(chunk: str):
                writer({"custom_llm_chunk": chunk})
            
            clarification_response = await client.chat_completion(
                messages=[
                    {"role": "system", "content": clarification_prompt}
                ],
                model="openai/gpt-4.1-mini",
                temperature=0.7,
                stream_callback=stream_callback
            )
            
            clarifying_question = clarification_response.get("content", "")
            
            state["needs_clarification"] = True
            state["clarification_attempts"] = clarification_attempts + 1
            state["current_response"] = clarifying_question
            
            # Append message to conversation history
            state["messages"].append({
                "role": "assistant",
                "content": clarifying_question
            })
            
        else:
            # Input is clear enough or max attempts reached
            response = "Thank you for the information. Let me help you with your IT issue."
            
            # Stream the static response
            writer({"custom_llm_chunk": response})
            
            state["needs_clarification"] = False
            state["current_response"] = response
            
            # Append message to conversation history
            state["messages"].append({
                "role": "assistant",
                "content": response
            })
    
    except Exception as e:
        # Error response
        error_response = "I'll help you with your IT issue. Let me analyze your request."
        
        # Stream the error response
        writer = get_stream_writer()
        writer({"custom_llm_chunk": error_response})
        
        state["needs_clarification"] = False
        state["current_response"] = error_response
        
        # Append message to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": error_response
        })
    
    return state
```

### Conditional Logic

The key to the conditional loop is the predicate function that determines whether to loop back to clarification or proceed to classification:

```python
def should_continue_clarifying(state) -> str:
    """Predicate function for conditional edge"""
    if state.get("needs_clarification", False):
        return "clarify"  # Loop back to clarify
    else:
        return "classify"  # Proceed to classification
```

This function will be used in the workflow definition to create the conditional edge.

## 2. classify_issue Node

### Purpose
Categorize the IT issue into one of the predefined categories: hardware, software, access, or other.

### Implementation

```python
async def classify_issue_node(state: SupportDeskState) -> SupportDeskState:
    """
    Categorize the IT issue into one of the predefined categories.
    
    This node:
    1. Analyzes the user's issue description
    2. Categorizes into: hardware, software, access, other
    3. Sets appropriate confidence levels
    4. Updates the workflow state with category information
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with category information
    """
    
    state = deepcopy(state)
    
    # Extract conversation history for context
    messages = state.get("messages", [])
    conversation_history = "\n".join([
        f"{msg.get('role', 'user')}: {msg.get('content', '')}" 
        for msg in messages
    ])
    
    try:
        # Get stream writer for custom streaming
        writer = get_stream_writer()
        
        # Prepare classification prompt
        classification_prompt = CLASSIFICATION_PROMPT.format(
            conversation_history=conversation_history
        )
        
        # Stream callback to emit chunks as they come in
        def stream_callback(chunk: str):
            writer({"custom_llm_chunk": chunk})
        
        # Call LLM to classify the issue
        classification_response = await client.chat_completion(
            messages=[
                {"role": "system", "content": classification_prompt}
            ],
            model="openai/gpt-4.1-mini",
            temperature=0.3,
            stream_callback=stream_callback
        )
        
        # Parse the classification response
        classification_content = classification_response.get("content", "")
        
        # Extract category from response
        # This is a simplified implementation - in a real system, we would use
        # structured output parsing or function calling
        if "hardware" in classification_content.lower():
            category = "hardware"
        elif "software" in classification_content.lower():
            category = "software"
        elif "access" in classification_content.lower():
            category = "access"
        else:
            category = "other"
        
        # Update state with classification information
        state["issue_category"] = category
        state["current_response"] = classification_content
        
        # Append message to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": classification_content
        })
        
    except Exception as e:
        # Error response
        error_response = "I'm analyzing your issue. Moving to the next step..."
        
        # Stream the error response
        writer = get_stream_writer()
        writer({"custom_llm_chunk": error_response})
        
        state["issue_category"] = "unknown"
        state["current_response"] = error_response
        
        # Append message to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": error_response
        })
    
    return state
```

## 3. triage_issue Node

### Purpose
Route the issue to the appropriate support team based on the category and priority.

### Implementation

```python
async def triage_issue_node(state: SupportDeskState) -> SupportDeskState:
    """
    Route the issue to the appropriate support team.
    
    This node:
    1. Determines the appropriate support team based on category
    2. Assesses priority based on business impact
    3. Routes to: L1 support, specialist, escalation
    4. Updates the workflow state with routing information
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with routing information
    """
    
    state = deepcopy(state)
    
    # Extract relevant information
    category = state.get("issue_category", "unknown")
    messages = state.get("messages", [])
    
    # Build conversation history for context
    conversation_history = "\n".join([
        f"{msg.get('role', 'user')}: {msg.get('content', '')}" 
        for msg in messages
    ])
    
    try:
        # Get stream writer for custom streaming
        writer = get_stream_writer()
        
        # Prepare triage prompt
        triage_prompt = TRIAGE_PROMPT.format(
            category=category,
            conversation_history=conversation_history
        )
        
        # Stream callback to emit chunks as they come in
        def stream_callback(chunk: str):
            writer({"custom_llm_chunk": chunk})
        
        # Call LLM to triage the issue
        triage_response = await client.chat_completion(
            messages=[
                {"role": "system", "content": triage_prompt}
            ],
            model="openai/gpt-4.1-mini",
            temperature=0.3,
            stream_callback=stream_callback
        )
        
        # Parse the triage response
        triage_content = triage_response.get("content", "")
        
        # Extract priority and support team from response
        # This is a simplified implementation
        if "high" in triage_content.lower() or "urgent" in triage_content.lower():
            priority = "high"
        elif "medium" in triage_content.lower():
            priority = "medium"
        else:
            priority = "low"
        
        # Determine support team based on category and priority
        if category == "hardware":
            support_team = "L1-Hardware"
        elif category == "software":
            support_team = "L2-Software"
        elif category == "access":
            support_team = "Security-Team"
        else:
            support_team = "General-Support"
        
        # For high priority issues, escalate
        if priority == "high":
            support_team = f"Escalated-{support_team}"
        
        # Update state with triage information
        state["issue_priority"] = priority
        state["support_team"] = support_team
        state["current_response"] = triage_content
        
        # Append message to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": triage_content
        })
        
    except Exception as e:
        # Error response
        error_response = "I'm determining the priority of your issue and routing it to the appropriate team."
        
        # Stream the error response
        writer = get_stream_writer()
        writer({"custom_llm_chunk": error_response})
        
        state["issue_priority"] = "medium"  # Default priority
        state["support_team"] = "General-Support"  # Default team
        state["current_response"] = error_response
        
        # Append message to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": error_response
        })
    
    return state
```

## 4. gather_info Node

### Purpose
Collect additional information needed for the support team to resolve the issue.

### Implementation

```python
async def gather_info_node(state: SupportDeskState) -> SupportDeskState:
    """
    Collect additional information needed for the support team.
    
    This node:
    1. Determines what information the support team needs
    2. Collects user details, context, urgency
    3. Updates the workflow state with complete ticket information
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with complete ticket information
    """
    
    state = deepcopy(state)
    
    # Extract relevant information
    category = state.get("issue_category", "unknown")
    priority = state.get("issue_priority", "medium")
    support_team = state.get("support_team", "General-Support")
    messages = state.get("messages", [])
    
    # Build conversation history for context
    conversation_history = "\n".join([
        f"{msg.get('role', 'user')}: {msg.get('content', '')}" 
        for msg in messages
    ])
    
    try:
        # Get stream writer for custom streaming
        writer = get_stream_writer()
        
        # Prepare info gathering prompt
        info_prompt = INFO_GATHERING_PROMPT.format(
            category=category,
            priority=priority,
            support_team=support_team,
            conversation_history=conversation_history
        )
        
        # Stream callback to emit chunks as they come in
        def stream_callback(chunk: str):
            writer({"custom_llm_chunk": chunk})
        
        # Call LLM to gather information
        info_response = await client.chat_completion(
            messages=[
                {"role": "system", "content": info_prompt}
            ],
            model="openai/gpt-4.1-mini",
            temperature=0.5,
            stream_callback=stream_callback
        )
        
        # Parse the information gathering response
        info_content = info_response.get("content", "")
        
        # Create ticket information dictionary
        ticket_info = {
            "category": category,
            "priority": priority,
            "support_team": support_team,
            "description": info_content,
            "timestamp": time.time(),
            "status": "new"
        }
        
        # Update state with ticket information
        state["ticket_info"] = ticket_info
        state["current_response"] = info_content
        
        # Append message to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": info_content
        })
        
    except Exception as e:
        # Error response
        error_response = "I'm gathering the necessary information for your support ticket."
        
        # Stream the error response
        writer = get_stream_writer()
        writer({"custom_llm_chunk": error_response})
        
        # Create minimal ticket information
        ticket_info = {
            "category": category,
            "priority": priority,
            "support_team": support_team,
            "description": "Issue requires attention",
            "timestamp": time.time(),
            "status": "new"
        }
        
        state["ticket_info"] = ticket_info
        state["current_response"] = error_response
        
        # Append message to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": error_response
        })
    
    return state
```

## 5. send_to_desk Node

### Purpose
Format the final response with ticket information and provide the user with confirmation and tracking info.

### Implementation

```python
async def send_to_desk_node(state: SupportDeskState) -> SupportDeskState:
    """
    Format the final response with ticket information.
    
    This node:
    1. Creates a simulated ticket ID
    2. Formats final response with ticket ID and next steps
    3. Creates professional handoff message
    4. Provides user confirmation and tracking info
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with final response
    """
    
    state = deepcopy(state)
    
    # Extract ticket information
    ticket_info = state.get("ticket_info", {})
    category = ticket_info.get("category", "unknown")
    priority = ticket_info.get("priority", "medium")
    support_team = ticket_info.get("support_team", "General-Support")
    
    try:
        # Get stream writer for custom streaming
        writer = get_stream_writer()
        
        # Generate a ticket ID
        ticket_id = f"T-{int(time.time())}-{random.randint(1000, 9999)}"
        
        # Prepare final response prompt
        final_prompt = FINAL_RESPONSE_PROMPT.format(
            ticket_id=ticket_id,
            category=category,
            priority=priority,
            support_team=support_team,
            ticket_info=json.dumps(ticket_info, indent=2)
        )
        
        # Stream callback to emit chunks as they come in
        def stream_callback(chunk: str):
            writer({"custom_llm_chunk": chunk})
        
        # Call LLM to generate final response
        final_response = await client.chat_completion(
            messages=[
                {"role": "system", "content": final_prompt}
            ],
            model="openai/gpt-4.1-mini",
            temperature=0.5,
            stream_callback=stream_callback
        )
        
        # Parse the final response
        final_content = final_response.get("content", "")
        
        # Update state with final information
        state["ticket_id"] = ticket_id
        state["ticket_status"] = "created"
        state["current_response"] = final_content
        
        # Append message to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": final_content
        })
        
    except Exception as e:
        # Error response
        error_response = f"Your support ticket has been created. A support agent from {support_team} will assist you shortly."
        
        # Generate a fallback ticket ID
        ticket_id = f"T-{int(time.time())}-ERROR"
        
        # Stream the error response
        writer = get_stream_writer()
        writer({"custom_llm_chunk": error_response})
        
        state["ticket_id"] = ticket_id
        state["ticket_status"] = "created_with_errors"
        state["current_response"] = error_response
        
        # Append message to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": error_response
        })
    
    return state
```

## Node Implementation Considerations

### Async Implementation

All nodes are implemented as async functions to support:
- Asynchronous LLM calls
- Streaming responses
- Non-blocking workflow execution

### Error Handling

Each node includes comprehensive error handling to ensure the workflow can continue even if a node encounters an error. This is important for educational purposes to demonstrate robust implementation.

### Streaming

The implementation uses streaming responses to provide a more interactive experience. Each node:
1. Gets a stream writer
2. Sets up a stream callback
3. Passes the callback to the LLM client
4. Updates the state with the streamed response

### State Management

Each node follows these state management principles:
1. Create a deep copy of the state to avoid side effects
2. Extract required information from the state
3. Process the information and generate a response
4. Update the state with new information
5. Return the updated state

### Conversation History

The conversation history is maintained in the state and used for context in each node. This ensures that the LLM has access to the full conversation when generating responses.

### Simplified Implementation

For educational purposes, the implementation is simplified compared to a production system:
- String matching is used instead of structured output parsing
- Error handling is basic but comprehensive
- The workflow is linear with a single conditional loop
- No external API calls are made

## Educational Considerations

Each node implementation includes:
1. Clear docstrings explaining the purpose and functionality
2. Comments explaining key steps and decisions
3. Simplified logic for educational clarity
4. Error handling to demonstrate robust implementation
5. Streaming to demonstrate interactive responses

The implementation is designed to be easily understood by students while still demonstrating best practices for LangGraph workflow development.