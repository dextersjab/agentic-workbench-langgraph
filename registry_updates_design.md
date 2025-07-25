# Registry Updates Design for IT Service Desk

## Overview

This document outlines the necessary updates to the workflow registry to replace the existing HelpHub workflow with the new Support Desk workflow. The registry is responsible for managing available workflows and models, making them accessible to the API.

## Current Registry Implementation

The current registry is implemented in `src/workflows/registry.py` and provides the following functionality:

1. Registering workflows with `register_workflow`
2. Retrieving workflows with `get_workflow`
3. Listing available models with `get_available_models`
4. Getting model information with `get_model_info`
5. Listing registered workflows with `list_workflows`

## Required Updates

To replace HelpHub with the Support Desk workflow, we need to make the following updates:

1. Update the lazy loading logic in `get_workflow`
2. Update the available models in the `_models` dictionary
3. Add any necessary imports for the Support Desk workflow

## Detailed Implementation

Here's the detailed implementation of the updated registry:

```python
"""
Workflow registry for managing available workflows and models.
"""
import logging
from typing import Dict, List, Any
from ..core.models import ModelInfo

logger = logging.getLogger(__name__)


class WorkflowRegistry:
    """
    Central registry for managing workflows and models.
    """
    
    _workflows: Dict[str, Any] = {}
    _models = {
        "support-desk-v1": ModelInfo(
            id="support-desk-v1",
            object="model",
            created=1234567890,
            owned_by="support-desk"
        ),
        "support-desk-advanced": ModelInfo(
            id="support-desk-advanced",
            object="model", 
            created=1234567890,
            owned_by="support-desk"
        )
    }
    
    @classmethod
    def register_workflow(cls, name: str, workflow_factory):
        """
        Register a workflow factory function.
        """
        cls._workflows[name] = workflow_factory
        logger.info(f"Registered workflow: {name}")
    
    @classmethod
    def get_workflow(cls, name: str):
        """
        Get a workflow instance by name.
        """
        if name not in cls._workflows:
            # Lazy load the Support Desk workflow
            if name == "support_desk":
                from .support_desk.workflow import create_support_desk_workflow
                workflow = create_support_desk_workflow()
                cls.register_workflow(name, lambda: workflow)
                return workflow
            else:
                # Default to support_desk workflow
                name = "support_desk"
                from .support_desk.workflow import create_support_desk_workflow
                workflow = create_support_desk_workflow()
                cls.register_workflow(name, lambda: workflow)
                return workflow
            
        workflow_factory = cls._workflows[name]
        if callable(workflow_factory):
            workflow = workflow_factory()
        else:
            workflow = workflow_factory
        logger.info(f"Created workflow instance: {name}")
        return workflow
    
    @classmethod
    def get_available_models(cls) -> List[ModelInfo]:
        """
        Get list of available models for Open WebUI.
        """
        return list(cls._models.values())
    
    @classmethod
    def get_model_info(cls, model_id: str) -> ModelInfo:
        """
        Get information about a specific model.
        """
        if model_id not in cls._models:
            # Default to first available model
            model_id = list(cls._models.keys())[0]
            
        return cls._models[model_id]
    
    @classmethod
    def list_workflows(cls) -> List[str]:
        """
        List all registered workflows.
        """
        return list(cls._workflows.keys())


logger.info("Workflow registry initialized")
```

## Key Changes

### 1. Updated Model Names

The model names have been updated to reflect the new Support Desk workflow:

```python
_models = {
    "support-desk-v1": ModelInfo(
        id="support-desk-v1",
        object="model",
        created=1234567890,
        owned_by="support-desk"
    ),
    "support-desk-advanced": ModelInfo(
        id="support-desk-advanced",
        object="model", 
        created=1234567890,
        owned_by="support-desk"
    )
}
```

This replaces the previous "helphub-v1" and "helphub-advanced" models.

### 2. Updated Lazy Loading Logic

The lazy loading logic in `get_workflow` has been updated to load the Support Desk workflow:

```python
# Lazy load the Support Desk workflow
if name == "support_desk":
    from .support_desk.workflow import create_support_desk_workflow
    workflow = create_support_desk_workflow()
    cls.register_workflow(name, lambda: workflow)
    return workflow
else:
    # Default to support_desk workflow
    name = "support_desk"
    from .support_desk.workflow import create_support_desk_workflow
    workflow = create_support_desk_workflow()
    cls.register_workflow(name, lambda: workflow)
    return workflow
```

This replaces the previous logic that loaded the HelpHub workflow.

## Integration with API

The API will continue to work as before, but now it will use the Support Desk workflow instead of HelpHub. The key integration point is in `api.py`:

```python
# Initialize Support Desk workflow state
state = create_initial_state()
workflow = WorkflowRegistry.get_workflow("support_desk")
```

The API doesn't need to be modified because it uses the registry to get the workflow, and we've updated the registry to return the Support Desk workflow.

## Educational Value

This registry design demonstrates several important concepts:

1. **Workflow Management**: How to register and retrieve workflows
2. **Lazy Loading**: How to load workflows only when needed
3. **Default Behavior**: How to provide fallbacks when requested workflows don't exist
4. **Model Management**: How to expose available models to the API

Students will learn:
- How to integrate new workflows into an existing system
- How to manage workflow and model registries
- How to implement lazy loading for efficient resource usage
- How to provide fallback behaviors for robustness

## Implementation Notes

The registry updates will be implemented in `src/workflows/registry.py` and will include:

1. Updated model names
2. Updated lazy loading logic
3. Any necessary imports for the Support Desk workflow

These changes will ensure that the API uses the Support Desk workflow instead of HelpHub, completing the replacement as specified in the requirements.