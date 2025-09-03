# Agentic Workflows Workbench

## Architecture
- **LangGraph workflow** for multi-step agentic behavior
- **Node naming convention**: `human_*` for HITL nodes (diamonds), descriptive names for LLM nodes (rectangles)
- **Three-way routing** from classify_issue: clarify → triage → escalate

## Workflow design principles
- LLM nodes handle analysis and question generation
- Human nodes (diamonds) handle interrupts and input collection only
- Questions are generated and streamed BEFORE state updates to work with LangGraph's checkpoint model

## Individual preferences
- @~/.claude/CLAUDE.md

## Learning and applying user taste

### Role understanding
The user is the **Taste Authority** - they define what feels right. Your role is to:
1. **Learn their taste** from corrections and preferences
2. **Internalize their standards** and apply them proactively
3. **Anticipate consistency needs** without being asked

### Taste learning process
When the user corrects something:
- Don't just fix that instance - understand the principle
- Look for other places where that principle applies
- Apply it proactively in future work

### Before considering work complete
Ask yourself:
- "Would this pass the user's taste test?"
- "What related details might the user notice?"
- "Am I being thorough in the way the user values?"

### Examples of taste patterns to learn:
- If user fixes one consistency issue, check for ALL similar inconsistencies
- If user reorders something for aesthetics, apply that ordering principle everywhere
- If user refines a name for clarity, consider all related names
- If user adjusts a comment, match that style throughout

### The goal
Apply consistency thoroughly within the current task. When you notice issues beyond the immediate scope, **ask** rather than assuming:
- "I noticed similar issues in [other files] - want me to address those?"
- "This pattern appears in [other places] - should I update them all?"

Obvious consistency (comments, formatting, naming within the same context) should just be handled. Questions are for scope expansion.