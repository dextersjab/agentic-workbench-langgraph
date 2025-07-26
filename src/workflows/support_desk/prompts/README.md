# Support desk workflow prompts

This directory contains the prompt templates used by each node in the IT Support Desk workflow. These prompts demonstrate effective prompt engineering techniques for different business tasks.

## Prompt overview

Each prompt is defined as a string constant that can be formatted with specific variables:

```python
EXAMPLE_PROMPT = """
You are an IT support specialist.

User Request: {user_input}
Conversation History: {conversation_history}

Respond with...
"""
```

## Prompt files

### [clarify_issue_prompt.py](clarify_issue_prompt.py)

Contains prompts for analysing input clarity and generating clarifying questions.

**Key prompts:**
- `ANALYSIS_PROMPT`: Determines if input needs clarification
- `CLARIFICATION_PROMPT`: Generates specific questions when needed

### [classify_issue_prompt.py](classify_issue_prompt.py)

Contains prompts for categorising IT issues into predefined types.

**Key prompts:**
- `CLASSIFICATION_PROMPT`: Categorises issues and sets priority

### [triage_issue_prompt.py](triage_issue_prompt.py)

Contains prompts for routing issues to appropriate support teams.

**Key prompts:**
- `TRIAGE_PROMPT`: Determines support team and response time

### [gather_info_prompt.py](gather_info_prompt.py)

Contains prompts for collecting additional information for support tickets.

**Key prompts:**
- `INFO_GATHERING_PROMPT`: Gathers comprehensive ticket details

### [send_to_desk_prompt.py](send_to_desk_prompt.py)

Contains prompts for formatting final responses with ticket information.

**Key prompts:**
- `FINAL_RESPONSE_PROMPT`: Creates professional handoff messages

## Prompt engineering techniques

Prompts follow the following structure:

1. **Define the role or objective**
   Establishing context, either through clear role:
   ```
   You are an IT support analyst reviewing a user's request...
   ```

   Or simply stating the objective:
   ```
   You are reviewing a user's request as part of an agentic support desk system...
   ```

2. **Explain the domain and situation**:
   Give the language model relevant information using variables in the prompt:
   ```
   User Request: {user_input}
   Conversation History: {conversation_history}
   ```

3. **Task specification**:
   Clearly defining the expected task:
   ```
   Analyse the request and determine if...
   ```

4. **Response format**:
   Specify the desired output structure:
   ```
   Respond with:
   - "CLEAR" if...
   - "NEEDS_CLARIFICATION" if...
   ```

   Or simply refer to a tool whose structure is described by its schema:
   ```
   Use the `Analysis` tool to set the `result` to:
     - "CLEAR" if you have sufficient information
     - "NEEDS_CLARIFICATION" if more details are required
   ```

5. **Guidelines and Constraints**: Shaping response characteristics
   ```
   Guidelines:
   - Ask for one specific piece of information at a time
   - Use simple, non-technical language
   ```
