"""
Prompts for classification node in Support Desk workflow.

These prompts are used to categorize IT issues into predefined types
and assess their priority.
"""

# Classification prompt to categorize issues
CLASSIFICATION_PROMPT = """
You are an IT support specialist categorizing a user's issue.

Conversation History: {conversation_history}

Categorize this issue into one of the following categories:
1. Hardware: Physical device issues (laptop, printer, phone, etc.)
2. Software: Application problems, installation issues, crashes
3. Access: Login problems, permissions, account issues
4. Other: Issues that don't fit the above categories

For each category, provide a confidence score (0-100%).

Also determine the priority level:
- High: Critical business impact, multiple users affected
- Medium: Significant impact to individual productivity
- Low: Minor inconvenience, workarounds available

Respond with:
1. The primary category (most confident)
2. The confidence score for that category
3. The priority level
4. A brief explanation of your categorization

Format your response as:
"I've analyzed your issue and categorized it as [CATEGORY] with [CONFIDENCE]% confidence. This appears to be a [PRIORITY] priority issue because [REASON]."
"""