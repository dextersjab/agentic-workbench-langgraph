"""Workflow utility functions."""
import logging

logger = logging.getLogger(__name__)


def create_workflow_initial_state(workflow_name: str):
    """
    Create initial state for a specific workflow.
    
    Args:
        workflow_name: Name of the workflow (e.g., "support-desk", "fs-agent")
        
    Returns:
        Initial state for the workflow
    """
    if workflow_name == "support-desk":
        from .support_desk.state import create_initial_state
        return create_initial_state()
    elif workflow_name == "fs-agent":
        from .fs_agent.state import create_initial_state
        return create_initial_state()
    else:
        # Default to support-desk for backward compatibility
        logger.warning(f"Unknown workflow {workflow_name}, defaulting to support-desk")
        from .support_desk.state import create_initial_state
        return create_initial_state()