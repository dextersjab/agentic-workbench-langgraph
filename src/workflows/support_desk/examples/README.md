# Support Desk Workflow Examples

This directory contains example conversations that demonstrate the IT Service Desk workflow in action. These examples showcase different user inputs and how the workflow responds, particularly highlighting the conditional clarification loop.

## Example Files

### [linear_flow.json](linear_flow.json)

Demonstrates the linear workflow when a user provides a clear request that doesn't need clarification.

**Key features:**
- Complete information in initial request
- No clarification needed
- Straight path through all nodes
- Professional ticket creation

**Sample conversation:**
```
User: My laptop won't connect to the company WiFi network. I've tried restarting it and forgetting the network, but it still won't connect. Other devices can connect fine, so it seems to be specific to my laptop. I need this fixed urgently as I have a client presentation this afternoon.

Support Desk: Thank you for the information. Let me help you with your IT issue.

[Workflow proceeds through classification, triage, information gathering, and ticket creation]
```

### [conditional_flow.json](conditional_flow.json)

Demonstrates the conditional loop when a user provides a vague request that needs clarification.

**Key features:**
- Vague initial request
- Multiple clarification questions
- Loop back to clarification node
- Eventually proceeds to classification

**Sample conversation:**
```
User: My computer isn't working right.

Support Desk: I'd be happy to help with your computer issue. To better assist you, could you please describe what specific problem you're experiencing? For example, is it not turning on, running slowly, showing error messages, or having trouble with specific applications?

User: It's really slow and keeps freezing when I try to open my email.

Support Desk: Thank you for that information. To help diagnose the issue better, could you tell me:
1. What email application are you using (Outlook, Gmail in browser, etc.)?
2. When did you first notice this problem?
3. Does your computer freeze only with email, or with other applications too?

[Conversation continues with clarification before proceeding]
```

### [max_attempts.json](max_attempts.json)

Demonstrates what happens when the maximum number of clarification attempts is reached without getting clear information.

**Key features:**
- Persistently vague user responses
- Maximum clarification attempts reached
- Workflow proceeds with limited information
- Generic support response

**Sample conversation:**
```
User: Something's not right.

Support Desk: I'd be happy to help you. Could you please provide more details about what isn't working correctly? Is this related to your computer, a specific application, network connection, or something else?

User: It's just not working.

[Multiple clarification attempts with vague responses]

Support Desk: Thank you for the information. Let me help you with your IT issue.

[Workflow proceeds with limited information]
```

## State Transitions

Each example includes detailed state transitions showing how the `SupportDeskState` evolves throughout the conversation. This helps students understand:

1. How state is maintained across multiple turns
2. How the `needs_clarification` flag controls the workflow path
3. How information is gradually collected and stored
4. How the final ticket is created

## Educational Value

These examples demonstrate:

1. **Conditional Logic**: How the workflow adapts based on input clarity
2. **Conversation Management**: How to handle multi-turn conversations
3. **State Tracking**: How to maintain context across interactions
4. **Graceful Degradation**: How to proceed even with limited information

## Using the Examples

These examples can be used for:

1. **Testing**: Verify that the workflow behaves as expected
2. **Learning**: Understand how the workflow handles different scenarios
3. **Debugging**: Identify issues in the implementation
4. **Demonstration**: Show the workflow in action to stakeholders

Students can modify these examples or create new ones to test different scenarios and edge cases.