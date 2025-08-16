"""
Read action node for fs_agent workflow.

This node executes read-only file operations (list, read).
"""
import os
import logging
from copy import deepcopy

from ..state import FSAgentState

logger = logging.getLogger(__name__)


async def read_act_node(state: FSAgentState) -> FSAgentState:
    """
    Execute a read action (list or read).
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with action result
    """
    state = deepcopy(state)
    
    # Get the planned action
    action = state["action"]["planned_action"]
    if not action:
        logger.warning("No planned action found in read_act")
        state["action"]["action_result"] = {
            "success": False,
            "result": None,
            "error": "No planned action found"
        }
        return state
    
    logger.info(f"Executing read action: {action['action_type']} on {action['path']}")
    
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
        if action["action_type"] == "list":
            # List files in directory
            if os.path.isdir(full_path):
                files = os.listdir(full_path)
                result = files if files else []
                success = True
                
                # Format result message
                if files:
                    file_list = "\n".join([f"  - {f}" for f in files])
                    message = f"Files in {path}:\n{file_list}"
                else:
                    message = f"The directory {path} is empty."
            else:
                error = f"Directory not found: {path}"
                message = error
                
        elif action["action_type"] == "read":
            # Read file contents
            if os.path.isfile(full_path):
                with open(full_path, 'r') as f:
                    content = f.read()
                result = content
                success = True
                
                # Format result message (truncate if too long)
                if len(content) > 1000:
                    preview = content[:1000] + "\n... (truncated)"
                else:
                    preview = content
                message = f"Contents of {path}:\n```\n{preview}\n```"
            else:
                error = f"File not found: {path}"
                message = error
        else:
            error = f"Invalid read action type: {action['action_type']}"
            message = error
            
    except PermissionError:
        error = f"Permission denied: {path}"
        message = error
    except Exception as e:
        error = f"Error executing read action: {str(e)}"
        message = error
    
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
    
    logger.info(f"Read action {'succeeded' if success else 'failed'}")
    
    return state