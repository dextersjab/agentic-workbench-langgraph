# Agentic Workflow Case Studies

## Overview

This project contains implementations of different agentic workflows designed as educational tools for teaching prompt engineering and LangGraph conditional logic. Each workflow is based on real business use cases and technical patterns.

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

## Agentic workflows in this project

- **[Support Desk](src/workflows/support_desk/README.md)** - IT service desk with conditional clarification loop

## Adding new workflows

To add a new workflow to the project:

1. Create a new directory under `src/workflows/` using underscores (e.g., `my_workflow/`)
2. Add a `workflow.py` file with a `create_workflow()` function that returns your LangGraph workflow
3. Add a model entry to the registry with the corresponding model ID using dashes (e.g., `"my-workflow"`)

The system will automatically discover and load workflows based on this convention:
- Model ID `"my-workflow"` maps to directory `src/workflows/my_workflow/`
- Each workflow must have `workflow.py` with `create_workflow()` function

## Getting started

To interact with the agentic systems:


Run the API:

```bash
python main.py
```


This will start the API server on port 8000, which you can interact with using the OpenAI API format.

Optionally, you can run the Open WebUI to interact with the workflow via a chat interface.

Run:

```shell
open-webui serve --port 3000
```

See [https://github.com/open-webui/open-webui]() for more details.
