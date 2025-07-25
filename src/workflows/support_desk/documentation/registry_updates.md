# Registry Updates Design for IT Service Desk

## Overview

This document outlines the necessary updates to the workflow registry to integrate the new Support Desk workflow. The registry is responsible for managing all available workflows and providing them to the API.

## Current Registry Implementation

The current registry is implemented in `src/workflows/registry.py` and provides the following functionality:

1. Registration of workflows
2. Retrieval of workflows by name
3. Listing of available models

## Required Updates

To integrate the Support Desk workflow, we need to make the following updates:

1. Update imports to include the Support Desk workflow
2. Register the Support Desk workflow with the registry
3. Update the default workflow to be the Support Desk workflow
4. Update the available models list to include the Support Desk model

## Detailed Implementation

Here's the detailed implementation of the updated registry:

```python
"""Workflow registry for managing available workflows."""
import logging
from typing import Dict, Any, List

from langchain_core.runnables import RunnableSequence

from .support_desk.workflow import create_support_desk_workflow
from .support_desk.state import SupportDeskState
from ..core.models import ModelInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowRegistry:
    """Registry for managing available workflows."""
    
    _workflows: Dict[str, RunnableSequence] = {}
    _default_workflow: str = "support_desk"
    
    @classmethod
    def register_workflow(cls, name: str, workflow: RunnableSequence) -> None:
        """Register a workflow with the registry.
        
        Args:
            name: The name of the workflow
            workflow: The workflow to register
        """
        logger.info(f"Registering workflow: {name}")
        cls._workflows[name] = workflow
    
    @classmethod
    def get_workflow(cls, name: str = None) -> RunnableSequence:
        """Get a workflow by name.
        
        Args:
            name: The name of the workflow to get. If None, returns the default workflow.
            
        Returns:
            The requested workflow
            
        Raises:
            KeyError: If the workflow is not found
        """
        if name is None:
            name = cls._default_workflow
            logger.info(f"No workflow name provided, using default: {name}")
        
        if name not in cls._workflows:
            logger.error(f"Workflow not found: {name}")
            raise KeyError(f"Workflow not found: {name}")
        
        logger.info(f"Returning workflow: {name}")
        return cls._workflows[name]
    
    @classmethod
    def get_available_models(cls) -> List[ModelInfo]:
        """Get a list of available models.
        
        Returns:
            A list of available models
        """
        logger.info("Getting available models")
        
        # Define the available models
        models = [
            ModelInfo(
                id="support-desk-it-agent",
                object="model",
                created=1625097600,
                owned_by="agentic-learning",
                root="support-desk-it-agent",
                parent=None,
                permission=[],
            )
        ]
        
        logger.info(f"Returning {len(models)} models")
        return models
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize the registry with available workflows."""
        logger.info("Initializing workflow registry")
        
        # Create and register the Support Desk workflow
        support_desk_workflow = create_support_desk_workflow()
        cls.register_workflow("support_desk", support_desk_workflow)
        
        logger.info("Workflow registry initialized")


# Initialize the registry when the module is imported
WorkflowRegistry.initialize()
```

## Key Changes

### 1. Updated Imports

The imports have been updated to use the Support Desk workflow:

```python
from .support_desk.workflow import create_support_desk_workflow
from .support_desk.state import SupportDeskState
```

This replaces the previous imports from HelpHub.

### 2. Updated Default Workflow

The default workflow has been updated to be the Support Desk workflow:

```python
_default_workflow: str = "support_desk"
```

This ensures that the API uses the Support Desk workflow by default.

### 3. Updated Available Models

The available models list has been updated to include the Support Desk model:

```python
models = [
    ModelInfo(
        id="support-desk-it-agent",
        object="model",
        created=1625097600,
        owned_by="agentic-learning",
        root="support-desk-it-agent",
        parent=None,
        permission=[],
    )
]
```

This replaces the previous HelpHub model.

### 4. Updated Initialization

The initialization method has been updated to create and register the Support Desk workflow:

```python
# Create and register the Support Desk workflow
support_desk_workflow = create_support_desk_workflow()
cls.register_workflow("support_desk", support_desk_workflow)
```

This ensures that the Support Desk workflow is available to the API.

## Integration Flow

When the application starts:

1. The registry is initialized
2. The Support Desk workflow is created and registered
3. The API can then retrieve the workflow by name

When a client makes a request to the API:

1. The API retrieves the Support Desk workflow from the registry
2. The workflow is executed with the client's input
3. The response is returned to the client

This flow is the same as before, but now it uses the Support Desk workflow instead of HelpHub.

## Educational Value

This registry design demonstrates several important concepts:

1. **Dependency Injection**: How to use a registry to manage dependencies
2. **Factory Pattern**: How to use factory functions to create workflows
3. **Singleton Pattern**: How to use a singleton registry to manage workflows
4. **Configuration Management**: How to configure the application to use different workflows

Students will learn:
- How to design a registry for managing workflows
- How to use factory functions to create workflows
- How to configure an application to use different workflows
- How to manage dependencies in a modular application

## Implementation Notes

The registry is implemented in `src/workflows/registry.py` and includes:

1. Updated imports
2. Updated default workflow
3. Updated available models
4. Updated initialization

These changes ensure that the registry uses the Support Desk workflow instead of HelpHub, completing the integration as specified in the requirements.