"""
Prompts for information gathering node in Support Desk workflow.

These prompts use tool calling to generate structured outputs.
"""

from ..kb.servicehub_policy import SERVICEHUB_SUPPORT_TICKET_POLICY

# Information gathering prompt using tool calling
INFO_GATHERING_PROMPT = """
You are a performing gathering comprehensive information for a support ticket as part of an IT support agentic workflow, working on behalf of ServiceHub.

ServiceHub Support Ticket Policy: {servicehub_support_ticket_policy}

Issue Category: {issue_category}
Issue Priority: {issue_priority}
Assigned Team: {support_team}
Conversation History: {conversation_history}

Analyse the conversation and extract comprehensive ticket information:

1. **Ticket Summary**: Create a concise, descriptive title for the issue
2. **Detailed Description**: Comprehensive description including symptoms, context, and timeline
3. **Affected Systems**: List specific systems, applications, or hardware mentioned
4. **User Impact**: How this issue affects the user's ability to work
5. **Reproduction Steps**: If applicable, steps to reproduce the issue
6. **Additional Context**: User role, department, location, or other relevant metadata

For {issue_category} issues, ensure you capture category-specific details:
- Hardware: Device models, error codes, physical symptoms
- Software: Application versions, error messages, workflows affected
- Access: Account names, systems involved, permission levels needed
- Network: Connection types, locations, devices affected

Provide a user-facing summary of the information gathered.

Use the {tool_name} tool to structure the ticket information.
"""