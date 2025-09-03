"""
Prompts for classification node in Support Desk workflow.

These prompts use tool calling to generate structured outputs.
"""

from .common import ESCALATION_PHRASES

# Classification prompt using tool calling
CLASSIFICATION_PROMPT = """
# Objective

You are part of an agentic system for IT Support Desk tasked with categorising a user's issue.

{servicehub_support_ticket_policy}

# Task

{task_instruction}

# Context

This is clarification attempt #{clarification_attempts} of {max_clarification_attempts}

{additional_context}

## Escalation Detection

{escalation_phrases}

If escalation is detected, set `user_requested_escalation=True` and attempt to classify with best guess.

## Classification Logic

If NOT escalating, determine if you have enough information to properly classify the issue.

If the user's input is:
- Too vague (e.g., "hi", "help", "I have a problem")
- Missing crucial details (no specific device, application, or error described)
- Unclear about the actual problem

Then set `needs_clarification=True`. You may leave category and priority as None if uncertain.

If you DO have sufficient information, categorise into one of these categories:
{issue_categories}

Priority levels:
{priority_levels}

This is the full conversation history between the IT Support Desk agentic system until now:
\"\"\"
{conversation_history}
\"\"\"

Use the {tool_name} tool to provide your analysis.
"""

# Format the prompt with escalation phrases
def format_classification_prompt(**kwargs):
    kwargs['escalation_phrases'] = ESCALATION_PHRASES
    return CLASSIFICATION_PROMPT.format(**kwargs)