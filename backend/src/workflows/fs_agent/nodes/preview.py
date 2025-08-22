"""
Preview node for fs_agent workflow.

This node generates previews and diffs for risky file operations
that require human approval before execution.
"""
import os
import logging
import difflib
from copy import deepcopy

from ..state import FSAgentState
from src.core.state_logger import log_node_start, log_node_complete
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)


def generate_unified_diff(original: str, modified: str, filename: str) -> str:
    """Generate a unified diff between original and modified content."""
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        modified.splitlines(keepends=True),
        fromfile=f"{filename} (current)",
        tofile=f"{filename} (proposed)",
        lineterm=""
    )
    return ''.join(diff)


def apply_edits(original_content: str, edits: list) -> str:
    """Apply a list of edit operations to the original content."""
    lines = original_content.splitlines()
    
    # Sort edits by line number (descending) to avoid index shifting issues
    sorted_edits = sorted(
        [edit for edit in edits if edit.get("line_number") is not None], 
        key=lambda x: x["line_number"], 
        reverse=True
    )
    
    # Apply line-based edits
    for edit in sorted_edits:
        line_num = edit["line_number"] - 1  # Convert to 0-based
        old_content = edit.get("old_content")
        new_content = edit["new_content"]
        
        if 0 <= line_num < len(lines):
            if old_content is None or lines[line_num] == old_content:
                lines[line_num] = new_content
            else:
                # Content mismatch - this should be handled as an error
                logger.warning(f"Line {line_num + 1} content mismatch. Expected: {old_content}, Found: {lines[line_num]}")
        else:
            logger.warning(f"Line number {line_num + 1} is out of range")
    
    # Apply append operations (no line number)
    append_edits = [edit for edit in edits if edit.get("line_number") is None]
    for edit in append_edits:
        lines.append(edit["new_content"])
    
    return '\n'.join(lines)


async def preview_node(state: FSAgentState) -> FSAgentState:
    """
    Generate a preview/diff for risky file operations requiring approval.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with preview content and approval requirements
    """
    state_before = deepcopy(state)
    state = deepcopy(state)
    
    # Log what this node will read from state
    log_node_start("preview", ["action.planned_action"], state)
    
    # Get stream writer for preview display
    writer = get_stream_writer()
    
    planned_action = state["action"]["planned_action"]
    if not planned_action:
        logger.warning("No planned action found in preview")
        state["approval"]["needs_approval"] = False
        state["approval"]["preview_content"] = ""
        
        # Log what this node wrote to state
        log_node_complete("preview", state_before, state)
        return state
    
    action_type = planned_action["action_type"]
    file_path = planned_action["path"]
    working_dir = state["session"]["working_directory"]
    
    # Normalize the path
    if not os.path.isabs(file_path):
        if file_path == working_dir or file_path.startswith(f"{working_dir}/"):
            full_path = file_path
        else:
            full_path = os.path.join(working_dir, file_path)
    else:
        full_path = file_path
    
    preview_content = ""
    
    try:
        if action_type == "delete":
            # Show what will be deleted
            if os.path.exists(full_path):
                if os.path.isfile(full_path):
                    # Read file to show what will be deleted
                    with open(full_path, 'r') as f:
                        content = f.read()
                    
                    preview_content = f"""## Delete Confirmation

**File to delete:** `{file_path}`

**Current content:**
```
{content}
```

⚠️  **This action cannot be undone!** ⚠️
"""
                else:
                    preview_content = f"""## Delete Confirmation

**Directory to delete:** `{file_path}`

⚠️  **This will delete the directory and all its contents!** ⚠️
"""
            else:
                preview_content = f"**Error:** File `{file_path}` does not exist."
        
        elif action_type == "write":
            # Check if file exists (overwrite scenario)
            if os.path.exists(full_path):
                with open(full_path, 'r') as f:
                    original_content = f.read()
                
                new_content = planned_action.get("content", "")
                diff = generate_unified_diff(original_content, new_content, file_path)
                
                preview_content = f"""## File Overwrite Preview

**File:** `{file_path}`

**Changes:**
```diff
{diff}
```

⚠️  **This will overwrite the existing file!** ⚠️
"""
            else:
                # New file creation
                new_content = planned_action.get("content", "")
                preview_content = f"""## New File Creation

**File:** `{file_path}`

**Content:**
```
{new_content}
```
"""
        
        elif action_type == "edit":
            # Show edit operations as diff
            if os.path.exists(full_path):
                with open(full_path, 'r') as f:
                    original_content = f.read()
                
                edits = planned_action.get("edits", [])
                if edits:
                    # Apply edits to generate modified content
                    modified_content = apply_edits(original_content, edits)
                    diff = generate_unified_diff(original_content, modified_content, file_path)
                    
                    preview_content = f"""## File Edit Preview

**File:** `{file_path}`

**Changes:**
```diff
{diff}
```
"""
                else:
                    preview_content = f"**Error:** No edit operations specified for `{file_path}`."
            else:
                preview_content = f"**Error:** Cannot edit non-existent file `{file_path}`."
        
        else:
            # Safe operations (list, read) don't need preview
            preview_content = f"Safe operation: {action_type} on `{file_path}`"
            state["approval"]["needs_approval"] = False
    
    except Exception as e:
        logger.error(f"Error generating preview: {e}")
        preview_content = f"**Error generating preview:** {str(e)}"
    
    # Update state with preview
    state["approval"]["preview_content"] = preview_content
    state["approval"]["needs_approval"] = action_type in ["delete", "write", "edit"]
    state["approval"]["approval_granted"] = False  # Reset approval
    
    # Stream the preview to user
    writer({"custom_llm_chunk": f"\n{preview_content}\n"})
    
    if state["approval"]["needs_approval"]:
        writer({"custom_llm_chunk": "\n**Do you want to proceed with this action? (yes/no)**\n"})
    
    logger.info(f"→ preview generated for {action_type} on {file_path}, needs_approval={state['approval']['needs_approval']}")
    
    # Log what this node wrote to state
    log_node_complete("preview", state_before, state)
    return state