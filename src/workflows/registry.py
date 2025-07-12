"""
Workflow registry for managing available workflows and models.

TODO for participants: Add additional workflows and customize
model configurations for your organization.
"""
import logging
from typing import Dict, List, Any
from ..core.models import ModelInfo

logger = logging.getLogger(__name__)


class WorkflowRegistry:
    """
    Central registry for managing workflows and models.
    
    TODO for participants:
    - Add additional workflow types (HR, Finance, etc.)
    - Implement workflow versioning
    - Add dynamic workflow loading
    - Include workflow health checks
    - Add A/B testing capabilities
    """
    
    _workflows: Dict[str, Any] = {}
    _models = {
        "helphub-v1": ModelInfo(
            id="helphub-v1",
            object="model",
            created=1234567890,
            owned_by="helphub"
        ),
        "helphub-advanced": ModelInfo(
            id="helphub-advanced",
            object="model", 
            created=1234567890,
            owned_by="helphub"
        )
    }
    
    @classmethod
    def register_workflow(cls, name: str, workflow_factory):
        """
        Register a workflow factory function.
        
        TODO for participants:
        - Add workflow validation
        - Implement version management
        - Add dependency checking
        - Include workflow metadata
        """
        cls._workflows[name] = workflow_factory
        logger.info(f"Registered workflow: {name}")
    
    @classmethod
    def get_workflow(cls, name: str):
        """
        Get a workflow instance by name.
        
        TODO for participants:
        - Add workflow caching
        - Implement lazy loading
        - Add error handling for missing workflows
        - Include workflow health checks
        """
        if name not in cls._workflows:
            # Lazy load the HelpHub workflow
            if name == "helphub":
                from .helphub.workflow import create_helphub_workflow
                workflow = create_helphub_workflow()
                cls.register_workflow(name, lambda: workflow)
                return workflow
            else:
                # Default to helphub workflow
                name = "helphub"
                from .helphub.workflow import create_helphub_workflow
                workflow = create_helphub_workflow()
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
        
        TODO for participants:
        - Add dynamic model discovery
        - Include model capabilities metadata
        - Add model health status
        - Implement model versioning
        """
        return list(cls._models.values())
    
    @classmethod
    def get_model_info(cls, model_id: str) -> ModelInfo:
        """
        Get information about a specific model.
        
        TODO for participants:
        - Add model capability descriptions
        - Include performance metrics
        - Add cost and usage information
        - Implement model comparison features
        """
        if model_id not in cls._models:
            # Default to first available model
            model_id = list(cls._models.keys())[0]
            
        return cls._models[model_id]
    
    @classmethod
    def list_workflows(cls) -> List[str]:
        """
        List all registered workflows.
        
        TODO for participants:
        - Add workflow metadata
        - Include status information
        - Add filtering capabilities
        - Implement workflow categories
        """
        return list(cls._workflows.keys())


# TODO for participants: Add your custom workflows here
# Example of how to add additional workflows:
# WorkflowRegistry.register_workflow("hr-support", create_hr_workflow)
# WorkflowRegistry.register_workflow("finance-support", create_finance_workflow)
# WorkflowRegistry.register_workflow("security-incident", create_security_workflow)

logger.info("Workflow registry initialized")