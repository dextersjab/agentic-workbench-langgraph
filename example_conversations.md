# Example Conversations for IT Service Desk

## Overview

This document provides example conversations that demonstrate the IT Service Desk workflow in action. These examples showcase both the linear flow (Phase 1) and the conditional loop (Phase 2) to help students understand how the workflow behaves in different scenarios.

## Example 1: Clear Request (Linear Flow)

This example demonstrates the linear flow when the user provides a clear request that doesn't need clarification.

### Conversation

**User:**
```
My laptop won't connect to the company WiFi network. I've tried restarting it and forgetting the network, but it still won't connect. Other devices can connect fine, so it seems to be specific to my laptop. I need this fixed urgently as I have a client presentation this afternoon.
```

**Support Desk (clarify_issue):**
```
Thank you for the information. Let me help you with your IT issue.
```

**Support Desk (classify_issue):**
```
I've analyzed your issue and categorized it as NETWORK with 95% confidence. This appears to be a HIGH priority issue because it's preventing you from connecting to essential resources and you have an urgent client presentation.
```

**Support Desk (triage_issue):**
```
I'm routing your issue to our L1-Network team with HIGH priority. You can expect a response within 1-2 hours. This routing is based on the network connectivity problem you're experiencing with your laptop.
```

**Support Desk (gather_info):**
```
# WiFi Connectivity Issue - Laptop Specific

## Issue Summary
User is unable to connect their laptop to the company WiFi network despite trying standard troubleshooting steps. Other devices can connect successfully, indicating a laptop-specific issue. This is time-sensitive due to an upcoming client presentation.

## Technical Details
- Device: Company laptop (additional details needed)
- Network: Company WiFi
- Troubleshooting attempted: Restart, forgetting network
- Error messages: None provided

## Business Impact
HIGH - User has a client presentation this afternoon and requires network access.

## Availability for Follow-up
User is available immediately for troubleshooting assistance.

## Additional Notes
Recommend immediate remote assistance to resolve before the presentation.
```

**Support Desk (send_to_desk):**
```
Your support ticket #T-1627384950-4321 has been created and assigned to our Network Support team with high priority.

A technician will contact you within the next 1-2 hours to help resolve your WiFi connectivity issue. Given the urgency of your presentation this afternoon, they'll prioritize getting you connected.

In the meantime, you might try:
- Connecting via ethernet cable if possible
- Using your phone as a hotspot temporarily
- Checking if there are any pending system updates

The Network Support team will reach out to you shortly. You can reference ticket #T-1627384950-4321 in any follow-up communications.

Thank you for your patience.
```

### State Transitions

1. **Initial State:**
   ```python
   {
       "messages": [],
       "current_user_input": "My laptop won't connect to the company WiFi network...",
       "needs_clarification": False,
       "clarification_attempts": 0,
       "max_clarification_attempts": 3,
       "issue_category": None,
       "issue_priority": None,
       "support_team": None,
       "ticket_info": {},
       "user_context": {},
       "current_response": "",
       "custom_llm_chunk": None,
       "ticket_id": None,
       "ticket_status": None
   }
   ```

2. **After clarify_issue:**
   ```python
   {
       "messages": [
           {"role": "user", "content": "My laptop won't connect to the company WiFi network..."},
           {"role": "assistant", "content": "Thank you for the information. Let me help you with your IT issue."}
       ],
       "current_user_input": "My laptop won't connect to the company WiFi network...",
       "needs_clarification": False,  # No clarification needed
       "clarification_attempts": 0,
       "max_clarification_attempts": 3,
       "issue_category": None,
       "issue_priority": None,
       "support_team": None,
       "ticket_info": {},
       "user_context": {},
       "current_response": "Thank you for the information. Let me help you with your IT issue.",
       "custom_llm_chunk": "Thank you for the information. Let me help you with your IT issue.",
       "ticket_id": None,
       "ticket_status": None
   }
   ```

3. **After classify_issue:**
   ```python
   {
       "messages": [
           {"role": "user", "content": "My laptop won't connect to the company WiFi network..."},
           {"role": "assistant", "content": "Thank you for the information. Let me help you with your IT issue."},
           {"role": "assistant", "content": "I've analyzed your issue and categorized it as NETWORK with 95% confidence..."}
       ],
       "current_user_input": "My laptop won't connect to the company WiFi network...",
       "needs_clarification": False,
       "clarification_attempts": 0,
       "max_clarification_attempts": 3,
       "issue_category": "network",  # Category set
       "issue_priority": "high",     # Priority set
       "support_team": None,
       "ticket_info": {},
       "user_context": {},
       "current_response": "I've analyzed your issue and categorized it as NETWORK with 95% confidence...",
       "custom_llm_chunk": "I've analyzed your issue and categorized it as NETWORK with 95% confidence...",
       "ticket_id": None,
       "ticket_status": None
   }
   ```

4. **After triage_issue:**
   ```python
   {
       "messages": [
           {"role": "user", "content": "My laptop won't connect to the company WiFi network..."},
           {"role": "assistant", "content": "Thank you for the information. Let me help you with your IT issue."},
           {"role": "assistant", "content": "I've analyzed your issue and categorized it as NETWORK with 95% confidence..."},
           {"role": "assistant", "content": "I'm routing your issue to our L1-Network team with HIGH priority..."}
       ],
       "current_user_input": "My laptop won't connect to the company WiFi network...",
       "needs_clarification": False,
       "clarification_attempts": 0,
       "max_clarification_attempts": 3,
       "issue_category": "network",
       "issue_priority": "high",
       "support_team": "L1-Network",  # Support team set
       "ticket_info": {},
       "user_context": {},
       "current_response": "I'm routing your issue to our L1-Network team with HIGH priority...",
       "custom_llm_chunk": "I'm routing your issue to our L1-Network team with HIGH priority...",
       "ticket_id": None,
       "ticket_status": None
   }
   ```

5. **After gather_info:**
   ```python
   {
       "messages": [
           {"role": "user", "content": "My laptop won't connect to the company WiFi network..."},
           {"role": "assistant", "content": "Thank you for the information. Let me help you with your IT issue."},
           {"role": "assistant", "content": "I've analyzed your issue and categorized it as NETWORK with 95% confidence..."},
           {"role": "assistant", "content": "I'm routing your issue to our L1-Network team with HIGH priority..."},
           {"role": "assistant", "content": "# WiFi Connectivity Issue - Laptop Specific..."}
       ],
       "current_user_input": "My laptop won't connect to the company WiFi network...",
       "needs_clarification": False,
       "clarification_attempts": 0,
       "max_clarification_attempts": 3,
       "issue_category": "network",
       "issue_priority": "high",
       "support_team": "L1-Network",
       "ticket_info": {  # Ticket info populated
           "category": "network",
           "priority": "high",
           "support_team": "L1-Network",
           "description": "# WiFi Connectivity Issue - Laptop Specific...",
           "timestamp": 1627384950,
           "status": "new"
       },
       "user_context": {},
       "current_response": "# WiFi Connectivity Issue - Laptop Specific...",
       "custom_llm_chunk": "# WiFi Connectivity Issue - Laptop Specific...",
       "ticket_id": None,
       "ticket_status": None
   }
   ```

6. **After send_to_desk:**
   ```python
   {
       "messages": [
           {"role": "user", "content": "My laptop won't connect to the company WiFi network..."},
           {"role": "assistant", "content": "Thank you for the information. Let me help you with your IT issue."},
           {"role": "assistant", "content": "I've analyzed your issue and categorized it as NETWORK with 95% confidence..."},
           {"role": "assistant", "content": "I'm routing your issue to our L1-Network team with HIGH priority..."},
           {"role": "assistant", "content": "# WiFi Connectivity Issue - Laptop Specific..."},
           {"role": "assistant", "content": "Your support ticket #T-1627384950-4321 has been created..."}
       ],
       "current_user_input": "My laptop won't connect to the company WiFi network...",
       "needs_clarification": False,
       "clarification_attempts": 0,
       "max_clarification_attempts": 3,
       "issue_category": "network",
       "issue_priority": "high",
       "support_team": "L1-Network",
       "ticket_info": {
           "category": "network",
           "priority": "high",
           "support_team": "L1-Network",
           "description": "# WiFi Connectivity Issue - Laptop Specific...",
           "timestamp": 1627384950,
           "status": "new"
       },
       "user_context": {},
       "current_response": "Your support ticket #T-1627384950-4321 has been created...",
       "custom_llm_chunk": "Your support ticket #T-1627384950-4321 has been created...",
       "ticket_id": "T-1627384950-4321",  # Ticket ID generated
       "ticket_status": "created"         # Ticket status updated
   }
   ```

## Example 2: Vague Request (Conditional Loop)

This example demonstrates the conditional loop when the user provides a vague request that needs clarification.

### Conversation

**User:**
```
My computer isn't working right.
```

**Support Desk (clarify_issue - first attempt):**
```
I'd be happy to help with your computer issue. To better assist you, could you please describe what specific problem you're experiencing? For example, is it not turning on, running slowly, showing error messages, or having trouble with specific applications?
```

**User:**
```
It's really slow and keeps freezing when I try to open my email.
```

**Support Desk (clarify_issue - second attempt):**
```
Thank you for that information. To help diagnose the issue better, could you tell me:
1. What email application are you using (Outlook, Gmail in browser, etc.)?
2. When did you first notice this problem?
3. Does your computer freeze only with email, or with other applications too?
```

**User:**
```
I'm using Outlook. It started yesterday after the system update. The computer is generally slow but freezes completely when I open Outlook.
```

**Support Desk (clarify_issue - final response):**
```
Thank you for the information. Let me help you with your IT issue.
```

**Support Desk (classify_issue):**
```
I've analyzed your issue and categorized it as SOFTWARE with 90% confidence. This appears to be a MEDIUM priority issue because it's preventing you from accessing your email, which is an essential work tool, and the issue began after a system update.
```

**Support Desk (triage_issue):**
```
I'm routing your issue to our L2-Software team with MEDIUM priority. You can expect a response within 4-8 hours. This routing is based on the software issue you're experiencing with Outlook following a system update.
```

**Support Desk (gather_info):**
```
# Outlook Freezing After System Update

## Issue Summary
User is experiencing system slowness and complete freezing when attempting to open Outlook. The issue began after a system update that was installed yesterday.

## Technical Details
- Application: Microsoft Outlook
- System: Company computer (additional details needed)
- Timing: Started after system update yesterday
- Symptoms: General slowness, complete freezing when opening Outlook
- Error messages: None reported

## Troubleshooting Attempted
None reported

## Business Impact
MEDIUM - User is unable to access email, which is an essential work tool.

## Availability for Follow-up
User is available for troubleshooting assistance.

## Additional Notes
Issue appears to be related to recent system update, suggesting potential compatibility issues or corrupted Outlook profile.
```

**Support Desk (send_to_desk):**
```
Your support ticket #T-1627385150-5678 has been created and assigned to our Software Support team with medium priority.

A technician will contact you within the next 4-8 hours to help resolve your Outlook freezing issue. Since this started after a system update, they'll focus on potential compatibility issues.

In the meantime, you might try:
- Restarting your computer if you haven't already
- Running Outlook in safe mode (hold Ctrl while opening Outlook)
- Checking if there are any pending updates

The Software Support team will reach out to you shortly. You can reference ticket #T-1627385150-5678 in any follow-up communications.

Thank you for your patience.
```

### State Transitions

1. **Initial State:**
   ```python
   {
       "messages": [],
       "current_user_input": "My computer isn't working right.",
       "needs_clarification": False,
       "clarification_attempts": 0,
       "max_clarification_attempts": 3,
       "issue_category": None,
       "issue_priority": None,
       "support_team": None,
       "ticket_info": {},
       "user_context": {},
       "current_response": "",
       "custom_llm_chunk": None,
       "ticket_id": None,
       "ticket_status": None
   }
   ```

2. **After clarify_issue (first attempt):**
   ```python
   {
       "messages": [
           {"role": "user", "content": "My computer isn't working right."},
           {"role": "assistant", "content": "I'd be happy to help with your computer issue..."}
       ],
       "current_user_input": "My computer isn't working right.",
       "needs_clarification": True,  # Needs clarification
       "clarification_attempts": 1,  # First attempt
       "max_clarification_attempts": 3,
       "issue_category": None,
       "issue_priority": None,
       "support_team": None,
       "ticket_info": {},
       "user_context": {},
       "current_response": "I'd be happy to help with your computer issue...",
       "custom_llm_chunk": "I'd be happy to help with your computer issue...",
       "ticket_id": None,
       "ticket_status": None
   }
   ```

3. **After user response and clarify_issue (second attempt):**
   ```python
   {
       "messages": [
           {"role": "user", "content": "My computer isn't working right."},
           {"role": "assistant", "content": "I'd be happy to help with your computer issue..."},
           {"role": "user", "content": "It's really slow and keeps freezing when I try to open my email."},
           {"role": "assistant", "content": "Thank you for that information. To help diagnose the issue better..."}
       ],
       "current_user_input": "It's really slow and keeps freezing when I try to open my email.",
       "needs_clarification": True,  # Still needs clarification
       "clarification_attempts": 2,  # Second attempt
       "max_clarification_attempts": 3,
       "issue_category": None,
       "issue_priority": None,
       "support_team": None,
       "ticket_info": {},
       "user_context": {},
       "current_response": "Thank you for that information. To help diagnose the issue better...",
       "custom_llm_chunk": "Thank you for that information. To help diagnose the issue better...",
       "ticket_id": None,
       "ticket_status": None
   }
   ```

4. **After user response and clarify_issue (final response):**
   ```python
   {
       "messages": [
           {"role": "user", "content": "My computer isn't working right."},
           {"role": "assistant", "content": "I'd be happy to help with your computer issue..."},
           {"role": "user", "content": "It's really slow and keeps freezing when I try to open my email."},
           {"role": "assistant", "content": "Thank you for that information. To help diagnose the issue better..."},
           {"role": "user", "content": "I'm using Outlook. It started yesterday after the system update..."},
           {"role": "assistant", "content": "Thank you for the information. Let me help you with your IT issue."}
       ],
       "current_user_input": "I'm using Outlook. It started yesterday after the system update...",
       "needs_clarification": False,  # No more clarification needed
       "clarification_attempts": 2,
       "max_clarification_attempts": 3,
       "issue_category": None,
       "issue_priority": None,
       "support_team": None,
       "ticket_info": {},
       "user_context": {},
       "current_response": "Thank you for the information. Let me help you with your IT issue.",
       "custom_llm_chunk": "Thank you for the information. Let me help you with your IT issue.",
       "ticket_id": None,
       "ticket_status": None
   }
   ```

5. **After classify_issue:**
   ```python
   {
       "messages": [
           {"role": "user", "content": "My computer isn't working right."},
           {"role": "assistant", "content": "I'd be happy to help with your computer issue..."},
           {"role": "user", "content": "It's really slow and keeps freezing when I try to open my email."},
           {"role": "assistant", "content": "Thank you for that information. To help diagnose the issue better..."},
           {"role": "user", "content": "I'm using Outlook. It started yesterday after the system update..."},
           {"role": "assistant", "content": "Thank you for the information. Let me help you with your IT issue."},
           {"role": "assistant", "content": "I've analyzed your issue and categorized it as SOFTWARE with 90% confidence..."}
       ],
       "current_user_input": "I'm using Outlook. It started yesterday after the system update...",
       "needs_clarification": False,
       "clarification_attempts": 2,
       "max_clarification_attempts": 3,
       "issue_category": "software",  # Category set
       "issue_priority": "medium",    # Priority set
       "support_team": None,
       "ticket_info": {},
       "user_context": {},
       "current_response": "I've analyzed your issue and categorized it as SOFTWARE with 90% confidence...",
       "custom_llm_chunk": "I've analyzed your issue and categorized it as SOFTWARE with 90% confidence...",
       "ticket_id": None,
       "ticket_status": None
   }
   ```

The remaining state transitions follow a similar pattern to Example 1, with the workflow proceeding through triage, information gathering, and ticket creation.

## Example 3: Max Clarification Attempts Reached

This example demonstrates what happens when the maximum number of clarification attempts is reached without getting clear information.

### Conversation

**User:**
```
Something's not right.
```

**Support Desk (clarify_issue - first attempt):**
```
I'd be happy to help you. Could you please provide more details about what isn't working correctly? Is this related to your computer, a specific application, network connection, or something else?
```

**User:**
```
It's just not working.
```

**Support Desk (clarify_issue - second attempt):**
```
I understand you're experiencing an issue. To help you effectively, I need to know what specifically isn't working. Is it your computer, phone, a software application, email, internet connection, or something else? Any details about error messages or when the problem started would also be helpful.
```

**User:**
```
The thing on my computer.
```

**Support Desk (clarify_issue - third attempt):**
```
Thank you for letting me know it's related to your computer. Could you please specify which program, application, or feature on your computer isn't working? For example, is it your web browser, email, a specific software, or perhaps the computer itself (like startup issues or performance problems)?
```

**User:**
```
The icon thing.
```

**Support Desk (clarify_issue - max attempts reached):**
```
Thank you for the information. Let me help you with your IT issue.
```

**Support Desk (classify_issue):**
```
I've analyzed your issue and categorized it as SOFTWARE with 60% confidence. This appears to be a LOW priority issue based on the limited information available. It seems to be related to an icon or application on your computer.
```

The workflow would continue with limited information, potentially resulting in a more generic response and requiring further clarification when the support team follows up.

## Educational Value

These example conversations demonstrate:

1. **Linear Flow**: When a user provides clear information, the workflow proceeds directly through all nodes without looping.

2. **Conditional Loop**: When a user provides vague information, the workflow loops through the clarification node until it has enough information or reaches the maximum number of attempts.

3. **State Management**: How the state evolves throughout the conversation, tracking information like clarification attempts, issue category, and ticket details.

4. **Prompt Engineering**: How different prompts are used at each stage to elicit specific information or generate appropriate responses.

Students can use these examples to understand:
- How the conditional loop works in practice
- How state is maintained across multiple turns of conversation
- How to design prompts that handle both clear and vague user inputs
- How to implement fallback mechanisms when ideal information isn't available

## Implementation Notes

These example conversations will be stored in JSON format in the `src/workflows/support_desk/examples/` directory:

1. `linear_flow.json`: Example 1 with clear request
2. `conditional_flow.json`: Example 2 with vague request
3. `max_attempts.json`: Example 3 with max clarification attempts reached

These files will include the complete conversation history and state transitions, providing a reference for testing and educational purposes.