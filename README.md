# IT Service Desk with Conditional Loop Pedagogy

## Overview

This project implements an IT Service Desk workflow with a conditional clarification loop, designed as an educational tool for teaching prompt engineering and LangGraph conditional logic.

## Learning Progression

The system supports a two-phase learning approach:

1. **Phase 1: Linear Workflow** - Focus on prompt engineering techniques
2. **Phase 2: Conditional Loop** - Focus on LangGraph conditional logic

## Project Structure

```
.
├── src/
│   └── workflows/
│       └── support_desk/         # Main workflow implementation
│           ├── nodes/            # Node implementations
│           ├── prompts/          # Prompt templates
│           └── examples/         # Example conversations
├── docs/                         # Detailed documentation
└── tests/                        # Test cases
```

## Key Components

- **[Workflow Architecture](support_desk_architecture.md)** - High-level design of the system
- **[State Management](state_management_design.md)** - How conversation state is tracked
- **[Node Implementations](node_implementations_design.md)** - The five workflow nodes
- **[Prompt Designs](prompt_designs.md)** - Templates for LLM interactions
- **[Implementation Plan](implementation_plan.md)** - Phased approach to building the system

## Getting Started

To run the IT Service Desk:

```bash
python main.py
```

This will start the API server on port 8000, which you can interact with using the OpenAI API format.

## Educational Resources

For instructors and students:

- **[Learning Outcomes](learning_outcomes.md)** - Educational goals and approach
- **[Example Conversations](example_conversations.md)** - Sample interactions demonstrating the workflow

## Business Topology

```
clarify ⟲ (conditional loop)
↓
classify → triage → gather_info → send_to_service_desk
```

## Next Steps

See the [Implementation Plan](implementation_plan.md) for details on how to implement this architecture.
