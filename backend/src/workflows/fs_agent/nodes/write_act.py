"""
Write action node for fs_agent workflow.

This node executes write operations (write, delete).
"""
import os
import logging
from copy import deepcopy

from ..state import FSAgentState

logger = logging.getLogger(__name__)


async def write_act_node(state: FSAgentState) -> FSAgentState:
    """
    Execute a write action (write or delete).
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with action result
    """
    state = deepcopy(state)
    
    # Get the planned action
    action = state["action"]["planned_action"]
    if not action:
        logger.warning("No planned action found in write_act")
        state["action"]["action_result"] = {
            "success": False,
            "result": None,
            "error": "No planned action found"
        }
        return state
    
    logger.info(f"Executing write action: {action['action_type']} on {action['path']}")
    
    # Normalize the path
    path = action["path"]
    working_dir = state["session"]["working_directory"]
    
    # Make path relative to working directory if not absolute
    if not os.path.isabs(path):
        if path == working_dir or path.startswith(f"{working_dir}/"):
            # Path already includes working directory
            full_path = path
        else:
            # Join with working directory
            full_path = os.path.join(working_dir, path)
    else:
        full_path = path
    
    # Execute the action
    result = None
    error = None
    success = False
    
    try:
        if action["action_type"] == "write":
            # Ensure directory exists
            dir_path = os.path.dirname(full_path)
            os.makedirs(dir_path, exist_ok=True)
            
            # Write content to file
            content = action.get("content", "")
            with open(full_path, 'w') as f:
                f.write(content)
            
            success = True
            result = f"Successfully wrote to {path}"
            message = f"✓ File written: {path}"
            
        elif action["action_type"] == "delete":
            # Delete file
            if os.path.isfile(full_path):
                os.remove(full_path)
                success = True
                result = f"Successfully deleted {path}"
                message = f"✓ File deleted: {path}"
            else:
                error = f"File not found: {path}"
                message = f"✗ Cannot delete: {error}"
        else:
            error = f"Invalid write action type: {action['action_type']}"
            message = f"✗ Error: {error}"
            
    except PermissionError:
        error = f"Permission denied: {path}"
        message = f"✗ Error: {error}"
    except Exception as e:
        error = f"Error executing write action: {str(e)}"
        message = f"✗ Error: {error}"
    
    # Update state with result
    state["action"]["action_result"] = {
        "success": success,
        "result": result,
        "error": error
    }
    
    # Add message to conversation
    state["messages"].append({
        "role": "assistant",
        "content": message
    })
    
    logger.info(f"Write action {'succeeded' if success else 'failed'}")
    
    return state