# Prompt Designs for IT Service Desk

## Overview

This document outlines the prompt designs for the Support Desk workflow. Each node in the workflow uses a specific prompt to generate responses and extract structured information. The prompts are designed to be modular, reusable, and educational.

## Prompt Structure

Each prompt follows a similar structure:

1. **System Message**: Provides context and instructions to the model
2. **User Message**: Contains the input data for the prompt
3. **Output Parser**: Extracts structured information from the model's response

## Prompt Implementations

### 1. clarify_issue_prompt

The `clarify_issue_prompt` is used by the `clarify_issue` node to ensure that the user's issue is clearly understood. It takes the user's input and generates a response that either confirms the issue or asks for clarification.

```python
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

Remember:
- Be professional and courteous
- Focus on understanding the technical issue
- Don't make assumptions about the issue
- If this is the {clarification_count} attempt (out of {max_clarification_attempts}), be more specific in your questions
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

clarify_issue_output_parser = StrOutputParser() | JsonOutputParser()
clarify_issue_prompt = clarify_issue_prompt | clarify_issue_output_parser
```

#### Expected Output

```json
{
  "issue_description": "User is unable to connect to the company VPN from their laptop",
  "needs_clarification": true,
  "response": "I understand you're having trouble connecting to the VPN. To help you better, could you please provide more details about: 1) What error message you're seeing, if any, 2) When this issue started, and 3) What steps you've already tried to resolve it?"
}
```

### 2. classify_issue_prompt

The `classify_issue_prompt` is used by the `classify_issue` node to categorize the issue and assign priority and complexity. It takes the issue description and generates a response that includes the issue category, priority, and complexity.

```python
classify_issue_system_message = """
You are an IT Service Desk assistant. Your task is to classify the user's issue by category, priority, and complexity.

Given the issue description, you should:
1. Determine the category of the issue (Hardware, Software, Network, Account/Access, Other)
2. Assign a priority level (Low, Medium, High, Critical)
3. Assess the complexity (Simple, Moderate, Complex)

Your response should include:
- The issue category
- The issue priority
- The issue complexity
- A brief explanation of your classification

Guidelines for classification:

Categories:
- Hardware: Issues with physical devices (computers, printers, phones)
- Software: Issues with applications, operating systems, or software updates
- Network: Issues with internet connectivity, VPN, or network resources
- Account/Access: Issues with logins, permissions, or access to systems
- Other: Issues that don't fit into the above categories

Priority levels:
- Low: Issue causes minor inconvenience, has workarounds, affects single user
- Medium: Issue impacts productivity, limited workarounds, affects small group
- High: Issue prevents work, no workarounds, affects department or critical function
- Critical: Issue affects business operations, security breach, affects entire organization

Complexity levels:
- Simple: Issue has a straightforward solution, requires minimal troubleshooting
- Moderate: Issue requires investigation, multiple possible causes, standard procedures exist
- Complex: Issue requires deep technical knowledge, multiple systems involved, custom solution needed
"""

classify_issue_user_message = """
Issue description: {issue_description}
"""

classify_issue_prompt = ChatPromptTemplate.from_messages([
    ("system", classify_issue_system_message),
    ("user", classify_issue_user_message)
])

classify_issue_output_parser = StrOutputParser() | JsonOutputParser()
classify_issue_prompt = classify_issue_prompt | classify_issue_output_parser
```

#### Expected Output

```json
{
  "issue_category": "Network",
  "issue_priority": "Medium",
  "issue_complexity": "Moderate",
  "response": "I've classified your VPN connection issue as follows:\n\n- Category: Network (since VPN is a network connectivity tool)\n- Priority: Medium (it impacts your productivity but likely has some workarounds)\n- Complexity: Moderate (requires investigation of multiple possible causes)\n\nThis classification will help us route your issue to the appropriate support team and prioritize it accordingly."
}
```

### 3. triage_issue_prompt

The `triage_issue_prompt` is used by the `triage_issue` node to determine what additional information is needed and which desk to assign the issue to. It takes the issue category, priority, and complexity and generates a response that includes the required information and desk assignment.

```python
triage_issue_system_message = """
You are an IT Service Desk assistant. Your task is to triage the user's issue by determining what additional information is needed and which desk to assign it to.

Given the issue category, priority, and complexity, you should:
1. Determine what additional information is needed to resolve the issue
2. Decide which service desk should handle the issue

Your response should include:
- A list of required information (specific questions or details needed)
- The desk assignment (which team should handle the issue)
- A brief explanation of your triage decision

Guidelines for triage:

Service Desks:
- Tier 1 Support: Handles simple issues across all categories
- Hardware Support: Handles moderate to complex hardware issues
- Software Support: Handles moderate to complex software issues
- Network Support: Handles moderate to complex network issues
- Security Team: Handles security-related issues or access problems
- Specialized Support: Handles complex issues requiring specialized knowledge

Required Information:
- Be specific about what information you need
- Focus on technical details relevant to the issue
- Consider what troubleshooting steps might have already been taken
- Ask for system specifications if relevant
- Request error messages or logs if applicable
"""

triage_issue_user_message = """
Issue category: {issue_category}
Issue priority: {issue_priority}
Issue complexity: {issue_complexity}
"""

triage_issue_prompt = ChatPromptTemplate.from_messages([
    ("system", triage_issue_system_message),
    ("user", triage_issue_user_message)
])

triage_issue_output_parser = StrOutputParser() | JsonOutputParser()
triage_issue_prompt = triage_issue_prompt | triage_issue_output_parser
```

#### Expected Output

```json
{
  "required_info": [
    "What VPN client software are you using?",
    "What error message do you see when trying to connect?",
    "Can you connect to other websites or network resources?",
    "Have you recently changed your network settings or updated your system?"
  ],
  "desk_assignment": "Network Support",
  "response": "Based on the classification of your issue as a Network problem with Medium priority and Moderate complexity, I'll need to gather some additional information before assigning it to our Network Support team. They specialize in VPN and connectivity issues and will be best equipped to help you resolve this problem."
}
```

### 4. gather_info_prompt

The `gather_info_prompt` is used by the `gather_info` node to collect additional information from the user. It takes the user's input, required information, and gathered information and generates a response that either asks for more information or confirms that all required information has been gathered.

```python
gather_info_system_message = """
You are an IT Service Desk assistant. Your task is to gather additional information from the user to help resolve their issue.

Given the user's input and the required information, you should:
1. Extract any relevant information from the user's input
2. Update the gathered information with the extracted information
3. Determine if all required information has been gathered
4. If clarification was requested, determine if the user's response provides the needed clarification

Your response should include:
- The updated gathered information
- Whether all required information has been gathered
- Whether clarification is still needed
- A response to the user (either asking for more information or confirming that all information has been gathered)

Remember:
- Be professional and courteous
- Ask one question at a time if possible
- Acknowledge the information the user has provided
- Be specific about what information you still need
"""

gather_info_user_message = """
User input: {user_input}

Required information: {required_info}
Gathered information: {gathered_info}
Needs clarification: {needs_clarification}
"""

gather_info_prompt = ChatPromptTemplate.from_messages([
    ("system", gather_info_system_message),
    ("user", gather_info_user_message)
])

gather_info_output_parser = StrOutputParser() | JsonOutputParser()
gather_info_prompt = gather_info_prompt | gather_info_output_parser
```

#### Expected Output

```json
{
  "gathered_info": {
    "VPN client software": "Cisco AnyConnect",
    "Error message": "Failed to establish connection. Reason: 413",
    "Can connect to other resources": "Yes"
  },
  "is_ready_for_desk": false,
  "needs_clarification": false,
  "response": "Thank you for providing that information. I see you're using Cisco AnyConnect and getting error 413 when trying to connect, although you can connect to other network resources. One more question: Have you recently changed any network settings or updated your system?"
}
```

### 5. send_to_desk_prompt

The `send_to_desk_prompt` is used by the `send_to_desk` node to generate the final response with the issue details and assignment. It takes all the information gathered during the conversation and generates a response that includes a summary of the issue and the next steps.

```python
send_to_desk_system_message = """
You are an IT Service Desk assistant. Your task is to generate a final response to the user with the issue details and assignment.

Given all the information gathered during the conversation, you should:
1. Summarize the issue and the information gathered
2. Inform the user which desk their issue has been assigned to
3. Provide an estimate of when they can expect a response
4. Thank the user for their patience

Your response should be professional, informative, and reassuring. Include:
- A summary of the issue
- The category, priority, and complexity of the issue
- The information gathered during the conversation
- The desk assignment
- Next steps and expected response time
- A thank you message
"""

send_to_desk_user_message = """
Issue description: {issue_description}
Issue category: {issue_category}
Issue priority: {issue_priority}
Issue complexity: {issue_complexity}
Gathered information: {gathered_info}
Desk assignment: {desk_assignment}
"""

send_to_desk_prompt = ChatPromptTemplate.from_messages([
    ("system", send_to_desk_system_message),
    ("user", send_to_desk_user_message)
])

send_to_desk_output_parser = StrOutputParser() | JsonOutputParser()
send_to_desk_prompt = send_to_desk_prompt | send_to_desk_output_parser
```

#### Expected Output

```json
{
  "response": "Thank you for providing all the necessary information about your VPN connection issue. Here's a summary of what we've gathered:\n\n- Issue: Unable to connect to the company VPN\n- Category: Network\n- Priority: Medium\n- Complexity: Moderate\n- VPN Client: Cisco AnyConnect\n- Error Message: Failed to establish connection. Reason: 413\n- Can connect to other resources: Yes\n- Recent system changes: Windows update installed yesterday\n\nYour issue has been assigned to our Network Support team. Given the priority and complexity, you can expect an initial response within 4 business hours. A support technician will contact you with troubleshooting steps or a solution.\n\nThank you for your patience. Your ticket number is #VPN-2023-07-25-001 for future reference."
}
```

## Educational Value

These prompt designs demonstrate several important concepts:

1. **Prompt Engineering**: How to design effective prompts for different business tasks
2. **Structured Output**: How to extract structured information from model responses
3. **Conversation Management**: How to manage a multi-turn conversation
4. **Business Logic**: How to implement business rules in prompts

Students will learn:
- How to design prompts for different business tasks
- How to extract structured information from model responses
- How to manage a multi-turn conversation
- How to implement business rules in prompts

## Implementation Notes

The prompts are implemented in `src/workflows/support_desk/prompts/` and include:

1. `clarify_issue_prompt.py`: Implementation of the `clarify_issue_prompt`
2. `classify_issue_prompt.py`: Implementation of the `classify_issue_prompt`
3. `triage_issue_prompt.py`: Implementation of the `triage_issue_prompt`
4. `gather_info_prompt.py`: Implementation of the `gather_info_prompt`
5. `send_to_desk_prompt.py`: Implementation of the `send_to_desk_prompt`

Each prompt is designed to be modular and reusable, allowing for easy modification and extension of the workflow.