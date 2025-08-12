# Agentic Workflows Workbench

## Architecture
- **LangGraph workflow** for multi-step agentic behavior
- **Node naming convention**: `human_*` for HITL nodes (diamonds), descriptive names for LLM nodes (rectangles)
- **Three-way routing** from classify_issue: clarify → triage → escalate

## Workflow Design Principles
- LLM nodes handle analysis and question generation
- Human nodes (diamonds) handle interrupts and input collection only
- Questions are generated and streamed BEFORE state updates to work with LangGraph's checkpoint model

## Individual prefernces
- @~/.claude/CLAUDE.md