"""
Workflow registry for managing available workflows and models.

Add additional workflows and customise model configurations for your agentic system use cases.
"""
import logging
import importlib
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
        ),
        "fs-agent": ModelInfo(
            id="fs-agent",
            object="model",
            created=1755309438,
            owned_by="fs-agent"
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
    def get_workflow(cls, name: str, checkpointer=None):
        """
        Get a workflow instance by name, optionally with a checkpointer.
        """
        if name not in cls._workflows:
            # Try to auto-discover workflow, passing the checkpointer
            cls._try_load_workflow(name, checkpointer)
        
        if name not in cls._workflows:
            logger.error(f"Unknown workflow: {name}")
            registered = list(cls._workflows.keys())
            if registered:
                raise ValueError(f"Unknown workflow: {name}. Registered workflows: {str(registered)[:200]}...")
            else:
                raise ValueError(f"No registered workflows found (searched for name '{name}')")
            
        # The factory is now a compiled graph instance from _try_load_workflow
        workflow = cls._workflows[name]
        logger.info(f"Retrieved workflow instance: {name}")
        return workflow
    
    @classmethod
    def _try_load_workflow(cls, name: str, checkpointer=None):
        """
        Try to auto-discover and compile a workflow, passing the checkpointer.
        """
        try:
            # Convert model name to directory name (support-desk -> support_desk)
            dir_name = name.replace('-', '_')
            module_name = f"src.workflows.{dir_name}.workflow"
            
            module = importlib.import_module(module_name)
            
            # Convention: each workflow must have create_workflow() function
            if hasattr(module, 'create_workflow'):
                create_func = getattr(module, 'create_workflow')
                
                # Pass the checkpointer to the factory function
                workflow = create_func(checkpointer=checkpointer)
                
                # Register the compiled workflow instance directly
                cls.register_workflow(name, workflow)
                logger.info(f"Auto-discovered and compiled workflow: {name}")
            else:
                logger.warning(f"No create_workflow() function found in {module_name}")
                
        except ImportError as e:
            logger.warning(f"Could not import workflow {name}: {e}")
        except Exception as e:
            logger.warning(f"Failed to load workflow {name}: {e}")
    
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