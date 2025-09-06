"""
Read action node for fs_agent workflow.

This node executes read-only file operations (list, read).
"""

import os
import logging
from copy import deepcopy

from ..state import FSAgentState
from src.core.state_logger import log_node_start, log_node_complete
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)


async def read_act_node(state: FSAgentState) -> FSAgentState:
    """
    Execute a read action (list or read).

    Args:
        state: Current workflow state

    Returns:
        Updated state with action result
    """
    state_before = deepcopy(state)

    # Log what this node will read from state
    log_node_start(
        "read_act", ["action.planned_action", "session.working_directory"], state
    )

    # Get stream writer for real-time feedback
    writer = get_stream_writer()

    # Get the planned action
    action = state["action"]["planned_action"]
    if not action:
        logger.warning("No planned action found in read_act")
        state["action"]["action_result"] = {
            "success": False,
            "result": None,
            "error": "No planned action found",
        }

        # Log what this node wrote to state
        log_node_complete("read_act", state_before, state)
        return state

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

                # Format and stream result message
                if files:
                    file_list = "\n".join([f"  - {f}" for f in files])
                    message = f"Files in {path}:\n{file_list}"
                else:
                    message = f"The directory {path} is empty."

                # Stream the directory listing
                writer({"custom_llm_chunk": f"\n{message}\n"})
            else:
                error = f"Directory not found: {path}"
                message = error
                # Stream error
                writer({"custom_llm_chunk": f"\n{message}\n"})

        elif action["action_type"] == "read":
            # Read file contents
            if os.path.isfile(full_path):
                with open(full_path, "r") as f:
                    content = f.read()
                result = content
                success = True

                # Format result message (truncate if too long)
                if len(content) > 1000:
                    preview = content[:1000] + "\n... (truncated)"
                else:
                    preview = content
                message = f"Contents of {path}:\n```\n{preview}\n```"

                # Stream the file contents
                writer({"custom_llm_chunk": f"\n{message}\n"})
            else:
                error = f"File not found: {path}"
                message = error
                # Stream error
                writer({"custom_llm_chunk": f"\n{message}\n"})
        else:
            error = f"Invalid read action type: {action['action_type']}"
            message = error
            # Stream error
            writer({"custom_llm_chunk": f"\n{message}\n"})

    except PermissionError:
        error = f"Permission denied: {path}"
        message = error
        # Stream error
        writer({"custom_llm_chunk": f"\n{message}\n"})
    except Exception as e:
        error = f"Error executing read action: {str(e)}"
        message = error
        # Stream error
        writer({"custom_llm_chunk": f"\n{message}\n"})

    # Update state with result
    state["action"]["action_result"] = {
        "success": success,
        "result": result,
        "error": error,
    }

    # Add message to conversation
    state["messages"].append({"role": "assistant", "content": message})

    # Log what this node wrote to state
    log_node_complete("read_act", state_before, state)
    return state
