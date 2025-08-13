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

### [classify_issue_prompt.py](classify_issue_prompt.py)

Contains prompts for categorising IT issues and generating clarifying questions.

**Key prompts:**
- `CLASSIFICATION_PROMPT`: Categorises issues and sets priority
- `GENERATE_QUESTION_PROMPT`: Generates clarifying questions when needed

### [route_issue_prompt.py](route_issue_prompt.py)

Contains prompts for routing issues to appropriate support teams.

**Key prompts:**
- `ROUTE_PROMPT`: Determines support team and response time

### [has_sufficient_info_prompt.py](has_sufficient_info_prompt.py)

Contains prompts for assessing information completeness.

**Key prompts:**
- `HAS_SUFFICIENT_INFO_PROMPT`: Assesses if enough information exists for ticket creation

### [generate_question_prompt.py](generate_question_prompt.py)

Contains prompts for generating targeted questions when more information is needed.

**Key prompts:**
- `GENERATE_QUESTION_PROMPT`: Creates specific questions based on context

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
