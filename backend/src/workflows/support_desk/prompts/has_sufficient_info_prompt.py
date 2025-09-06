"""
Prompts for has_sufficient_info node in Support Desk workflow.

These prompts use tool calling to generate structured outputs.
"""

from .common import ESCALATION_PHRASES

# Has sufficient info prompt using tool calling
HAS_SUFFICIENT_INFO_PROMPT = """
# Objective

You are part of an agentic system for IT Support Desk tasked with assessing if enough information has been gathered to create a comprehensive support ticket.

{servicehub_support_ticket_policy}

# Task

{task_instruction}

# Context

This is gathering round #{gathering_round} of {max_gathering_rounds}

{additional_context}

## Current Ticket State
- Issue Category: {issue_category}
- Issue Priority: {issue_priority}
- Assigned Team: {support_team}

## Escalation Detection

{escalation_phrases}

If escalation is detected, set `user_requested_escalation=True` and set needs_more_info=False.

## Assessment Logic

If NOT escalating, determine if you have enough information to create a comprehensive ticket.

{required_info_categories}

{category_specific_priorities}

Consider:
- Whether critical information is missing for proper ticket creation
- Issue priority and SLAs (P1 issues may need less detail to start resolution)
- User location, department, role (if relevant to issue)

## Examples of Sufficient Information

- "Sales colleagues can't access Salesforce CRM - getting 'service unavailable' error. This is blocking our quarterly deal closure calls."
  → Sufficient: specific system, error type, business impact

- "I can't log in to the Portal" + "started this morning" + "error says password invalid" + "working from Manchester office"
  → Sufficient: system, timeline, specific error, location

## Examples Needing More Info

- "Something is broken" → needs what system, what's happening
- "The Portal is slow" → needs specific performance issue, when it started, which function

This is the full conversation history between the IT Support Desk agentic system until now:
\"\"\"
{conversation_history}
\"\"\"

Use the {tool_name} tool to provide your assessment.
"""


# Format the prompt with escalation phrases
def format_has_sufficient_info_prompt(**kwargs):
    kwargs["escalation_phrases"] = ESCALATION_PHRASES
    return HAS_SUFFICIENT_INFO_PROMPT.format(**kwargs)
