"""
Utility functions for fs_agent workflow nodes.
"""
import logging

from ..state import FSAgentState

logger = logging.getLogger(__name__)


def is_finished(state: FSAgentState) -> bool:
    """
    Determine if the workflow is finished.
    
    Args:
        state: Current workflow state
        
    Returns:
        True if workflow should end, False otherwise
    """
    finished = state["session"]["is_finished"]
    logger.info(f"Checking if workflow is finished: {finished}")
    return finished