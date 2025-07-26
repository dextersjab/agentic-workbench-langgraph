# Agentic Workflow Case Studies

## Overview

This project contains implementations of different agentic workflows designed as educational tools for teaching prompt engineering and LangGraph conditional logic. Each workflow demonstrates specific business use cases and technical patterns.

## Project structure

```
.
├── src/
│   ├── core/                     # Core API and LLM infrastructure
│   └── workflows/                # Individual workflow implementations
│       └── support_desk/         # IT Service Desk workflow
│           ├── data/             # Sample data and conversations
│           ├── kb/               # Knowledge base articles
│           ├── docs/             # Workflow documentation
│           ├── nodes/            # Node implementations
│           ├── prompts/          # Prompt templates
│           └── examples/         # Example conversations
├── main.py                       # API server entry point
└── requirements.txt              # Python dependencies
```

## Available workflows

- **[Support Desk](src/workflows/support_desk/README.md)** - IT service desk with conditional clarification loop

## Getting started

To run the workflows:

```bash
python main.py
```

This will start the API server on port 8000, which you can interact with using the OpenAI API format.
