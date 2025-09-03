# fs_agent workflow prompts

This directory contains the prompt templates used by the reasoning nodes in the File System Agent workflow. These prompts guide the agent's observation and planning processes.

## Prompt overview

Prompts are defined as string templates that can be formatted with specific variables:

```python
EXAMPLE_PROMPT = """
You are a file system agent assistant.

Current context: {context}
User request: {user_request}

Analyze and respond...
"""
```

## Prompt files

### [observe_prompt.py](observe_prompt.py)

Contains prompts for the observation phase where the agent gathers context.

**Key prompts:**
- `OBSERVE_PROMPT`: Analyzes conversation history and extracts relevant context
- Focuses on understanding user intent and previous actions
- Structures observations for the planning phase

**Variables used:**
- `conversation_history`: Full conversation context
- `previous_actions`: Results from prior operations
- `workspace_status`: Current workspace state

### [plan_prompt.py](plan_prompt.py)

Contains prompts for the planning phase where the agent decides on actions.

**Key prompts:**
- `PLAN_PROMPT`: Main planning prompt that determines next action
- `THINK_PROMPT`: Used during thinking loops for complex reasoning
- `SAFETY_ASSESSMENT_PROMPT`: Classifies actions as safe or risky

**Variables used:**
- `observation`: Context from observe node
- `user_request`: Current user message
- `think_history`: Previous thinking iterations
- `available_actions`: Permitted operations

## Prompt engineering techniques

### 1. **Clear role definition**
```
You are a file system agent that helps users manage files in their workspace.
Your primary goal is to execute file operations safely and efficiently.
```

### 2. **Context injection**
Prompts include relevant context through variables:
```
Current observation: {observation}
Previous actions taken: {action_history}
Workspace directory: {workspace_dir}
```

### 3. **Structured reasoning**
Planning prompts guide step-by-step reasoning:
```
1. Analyze the user's request
2. Consider the current context
3. Determine if additional thinking is needed
4. Plan the appropriate action
5. Assess action safety (safe vs risky)
```

### 4. **Safety guidelines**
Prompts emphasize safety considerations:
```
Guidelines:
- Read operations are considered SAFE
- Write/Edit/Delete operations are RISKY and require approval
- Always validate file paths to prevent traversal attacks
- Provide clear previews for destructive operations
```

### 5. **Output structure**
Prompts specify structured outputs using tools/schemas:
```
Use the PlanOutput tool to structure your response:
- action_type: One of [list, read, write, edit, delete, none]
- file_path: Target file path (if applicable)
- content: File content (for write/edit operations)
- reasoning: Explanation of your decision
- needs_thinking: Whether deeper reasoning is required
- safety_classification: Either "safe" or "risky"
```

## Thinking loop mechanism

The plan prompt supports iterative thinking:

```python
# First iteration
"Analyze the request and determine if complex reasoning is needed..."

# Thinking loop (if triggered)
"Let's think through this step by step:
 Previous thought: {previous_reasoning}
 Now considering: ..."

# Final decision
"Based on the analysis, the best action is..."
```

## Safety classification logic

Prompts guide the agent to classify actions:

**Safe actions:**
- Listing directory contents
- Reading file contents
- Observing workspace state

**Risky actions:**
- Writing new files
- Editing existing files
- Deleting files
- Any operation that modifies state

## Best practices

1. **Explicit over implicit**: Prompts clearly state what constitutes safe vs risky
2. **Examples in context**: Include examples of proper file paths and operations
3. **Error guidance**: Prompts include how to handle edge cases
4. **User-friendly responses**: Guide agent to explain actions clearly
5. **Security first**: Emphasis on path validation and preview generation

## Prompt evolution

Prompts should evolve based on:
- User feedback on agent behavior
- Edge cases discovered during usage
- Security considerations
- Performance optimizations

When modifying prompts:
1. Test with various user inputs
2. Verify safety classifications remain accurate
3. Ensure thinking loops terminate properly
4. Validate structured outputs match schemas