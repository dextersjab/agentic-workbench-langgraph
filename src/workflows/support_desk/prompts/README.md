# Support Desk Workflow Prompts

This directory contains the prompt templates used by each node in the IT Service Desk workflow. These prompts demonstrate effective prompt engineering techniques for different business tasks.

## Prompt Overview

Each prompt is defined as a string constant that can be formatted with specific variables:

```python
EXAMPLE_PROMPT = """
You are an IT support specialist.

User Request: {user_input}
Conversation History: {conversation_history}

Respond with...
"""
```

## Prompt Files

### [clarify_issue_prompt.py](clarify_issue_prompt.py)

Contains prompts for analyzing input clarity and generating clarifying questions.

**Key prompts:**
- `ANALYSIS_PROMPT`: Determines if input needs clarification
- `CLARIFICATION_PROMPT`: Generates specific questions when needed

**Educational focus:**
- Input analysis techniques
- Question generation strategies
- Conversation management

### [classify_issue_prompt.py](classify_issue_prompt.py)

Contains prompts for categorizing IT issues into predefined types.

**Key prompts:**
- `CLASSIFICATION_PROMPT`: Categorizes issues and sets priority

**Educational focus:**
- Classification techniques
- Confidence scoring
- Multi-attribute extraction

### [triage_issue_prompt.py](triage_issue_prompt.py)

Contains prompts for routing issues to appropriate support teams.

**Key prompts:**
- `TRIAGE_PROMPT`: Determines support team and response time

**Educational focus:**
- Routing logic
- Priority-based decision making
- Response time estimation

### [gather_info_prompt.py](gather_info_prompt.py)

Contains prompts for collecting additional information for support tickets.

**Key prompts:**
- `INFO_GATHERING_PROMPT`: Gathers comprehensive ticket details

**Educational focus:**
- Information extraction
- Context-aware data collection
- Structured output generation

### [send_to_desk_prompt.py](send_to_desk_prompt.py)

Contains prompts for formatting final responses with ticket information.

**Key prompts:**
- `FINAL_RESPONSE_PROMPT`: Creates professional handoff messages

**Educational focus:**
- Response formatting
- Professional communication
- Expectation setting

## Prompt Engineering Techniques

These prompts demonstrate several key techniques:

1. **Role Definition**: Establishing context through clear roles
   ```
   You are an IT support analyst reviewing a user's request...
   ```

2. **Context Provision**: Providing relevant information through variables
   ```
   User Request: {user_input}
   Conversation History: {conversation_history}
   ```

3. **Task Specification**: Clearly defining the expected task
   ```
   Analyze the request and determine if...
   ```

4. **Response Format**: Specifying the desired output structure
   ```
   Respond with:
   - "CLEAR" if...
   - "NEEDS_CLARIFICATION" if...
   ```

5. **Guidelines and Constraints**: Shaping response characteristics
   ```
   Guidelines:
   - Ask for one specific piece of information at a time
   - Use simple, non-technical language
   ```

## Educational Value

Students can learn how to:
- Design prompts for specific business workflows
- Create prompts that generate consistent, structured outputs
- Use role definitions to guide LLM behavior
- Manage context effectively in multi-turn conversations
- Apply constraints to shape response characteristics