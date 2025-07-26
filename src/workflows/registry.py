"""
Workflow registry for managing available workflows and models.

Add additional workflows and customise model configurations for your agentic system use cases.
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
        "support-desk": ModelInfo(
            id="support-desk",
            object="model",
            created=1753056000,
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