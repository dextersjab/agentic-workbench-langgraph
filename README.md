# Agentic workflow workbench

## Overview

Run this API locally to build and experiment with agentic workflows with ease.

Connect to the popular frontend [Open WebUI](https://openwebui.com/) for a ChatGPT-like experience.

The workflows in this project are based on winning solutions to real enterprise challenges.

Feel free to take inspiration, modify and build your own!

## Project structure

```
.
├── src/
│   ├── core/                     # Shared API and LLM client code
│   └── workflows/
│       └── support_desk/         # Business use case: IT Support Desk workflow
├── main.py                       # API server entrypoint
└── requirements.txt
```

## Agentic workflows in this project

- **[IT Support Desk](src/workflows/support_desk/README.md)** - IT Support desk with conditional clarification loop

## Adding new workflows

To add a new workflow to the project:

1. Create a new directory under `src/workflows/` using underscores (e.g., `my_workflow/`)
2. Add a `workflow.py` file with a `create_workflow()` function that returns your LangGraph workflow
3. Add a model entry to the registry with the corresponding model ID using dashes (e.g., `"my-workflow"`)

The system will automatically discover and load workflows based on this convention:
- Model ID `"my-workflow"` maps to directory `src/workflows/my_workflow/`
- Each workflow must have `workflow.py` with `create_workflow()` function

## Getting started

Run the API server to interact with the agentic systems:

```bash
uvicorn src.core.api:app --reload --port 8000
```

You can interact with the server on [`http://localhost:8000`]() following commonly-used OpenAI-style request patterns.

Optionally, use the Open WebUI chat interface for a ChatGPT-like user experience:

```shell
open-webui serve --port 3000
```

The models will appear in the top-left corner dropdown.

See [https://github.com/open-webui/open-webui]() for more details.
