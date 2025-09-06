"""
Write action node for fs_agent workflow.

This node executes write operations (write, delete).
"""

import os
import logging
from copy import deepcopy

from ..state import FSAgentState
from src.core.state_logger import log_node_start, log_node_complete
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)


async def write_act_node(state: FSAgentState) -> FSAgentState:
    """
    Execute a write action (write or delete).

    Args:
        state: Current workflow state

    Returns:
        Updated state with action result
    """
    state_before = deepcopy(state)

    # Log what this node will read from state
    log_node_start(
        "write_act", ["action.planned_action", "session.working_directory"], state
    )

    # Get stream writer for real-time feedback
    writer = get_stream_writer()

    # Get the planned action
    action = state["action"]["planned_action"]
    if not action:
        logger.warning("No planned action found in write_act")
        state["action"]["action_result"] = {
            "success": False,
            "result": None,
            "error": "No planned action found",
        }

        # Log what this node wrote to state
        log_node_complete("write_act", state_before, state)
        return state

    # Check approval for risky operations
    approval = state["approval"]
    if approval["needs_approval"] and not approval["approval_granted"]:
        logger.warning(
            f"Action {action['action_type']} on {action['path']} was rejected by user"
        )
        state["action"]["action_result"] = {
            "success": False,
            "result": None,
            "error": "Action rejected by user",
        }

        # Stream rejection message
        writer({"custom_llm_chunk": "\n✗ Action cancelled: User did not approve\n"})

        # Add message to conversation
        state["messages"].append(
            {"role": "assistant", "content": "✗ Action cancelled: User did not approve"}
        )

        # Log what this node wrote to state
        log_node_complete("write_act", state_before, state)
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
        if action["action_type"] == "write":
            # Ensure directory exists
            dir_path = os.path.dirname(full_path)
            os.makedirs(dir_path, exist_ok=True)

            # Write content to file
            content = action.get("content", "")
            with open(full_path, "w") as f:
                f.write(content)

            success = True
            result = f"Successfully wrote to {path}"
            message = f"✓ File written: {path}"

            # Stream success message
            writer({"custom_llm_chunk": f"\n{message}\n"})

        elif action["action_type"] == "edit":
            # Apply edit operations to file
            if not os.path.exists(full_path):
                error = f"Cannot edit non-existent file: {path}"
                message = f"✗ Error: {error}"
                writer({"custom_llm_chunk": f"\n{message}\n"})
            else:
                # Read original content
                with open(full_path, "r") as f:
                    original_content = f.read()

                # Apply edits
                edits = action.get("edits", [])
                if edits:
                    # Import the edit function from preview node
                    from .preview import apply_edits

                    try:
                        modified_content = apply_edits(original_content, edits)

                        # Write modified content back
                        with open(full_path, "w") as f:
                            f.write(modified_content)

                        success = True
                        result = f"Successfully applied {len(edits)} edit(s) to {path}"
                        message = f"✓ File edited: {path} ({len(edits)} change(s))"

                        # Stream success message
                        writer({"custom_llm_chunk": f"\n{message}\n"})

                    except Exception as edit_error:
                        error = f"Error applying edits to {path}: {str(edit_error)}"
                        message = f"✗ Error: {error}"
                        writer({"custom_llm_chunk": f"\n{message}\n"})
                else:
                    error = f"No edit operations specified for {path}"
                    message = f"✗ Error: {error}"
                    writer({"custom_llm_chunk": f"\n{message}\n"})

        elif action["action_type"] == "delete":
            # Delete file
            if os.path.isfile(full_path):
                os.remove(full_path)
                success = True
                result = f"Successfully deleted {path}"
                message = f"✓ File deleted: {path}"

                # Stream success message
                writer({"custom_llm_chunk": f"\n{message}\n"})
            else:
                error = f"File not found: {path}"
                message = f"✗ Cannot delete: {error}"

                # Stream error message
                writer({"custom_llm_chunk": f"\n{message}\n"})
        else:
            error = f"Invalid write action type: {action['action_type']}"
            message = f"✗ Error: {error}"

            # Stream error message
            writer({"custom_llm_chunk": f"\n{message}\n"})

    except PermissionError:
        error = f"Permission denied: {path}"
        message = f"✗ Error: {error}"

        # Stream error message
        writer({"custom_llm_chunk": f"\n{message}\n"})
    except Exception as e:
        error = f"Error executing write action: {str(e)}"
        message = f"✗ Error: {error}"

        # Stream error message
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
    log_node_complete("write_act", state_before, state)
    return state
