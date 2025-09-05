"""
Observe node for fs_agent workflow.

This node observes the current state and gathers context for planning.
On first interaction, it determines if the session should be read-only or allow writes.
"""
import logging
from copy import deepcopy

from ..state import FSAgentState
from ..business_context import MAX_ACTION_REPETITIONS
from src.core.state_logger import log_node_start, log_node_complete
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)


async def observe_node(state: FSAgentState) -> FSAgentState:
    """
    Observe the current state and gather context for planning.
    On first interaction, determine read-only vs write mode based on user intent.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with observations and mode settings
    """
    state_before = deepcopy(state)
    
    # Log what this node will read from state
    log_node_start("observe", ["messages", "session", "action"], state)
    
    # Get stream writer for feedback
    writer = get_stream_writer()
    
    # Check if this is the first interaction
    is_first = state["session"]["is_first_interaction"]
    logger.info(f"→ observe called: is_first={is_first}")
    
    if is_first:
        # Determine mode based on user request
        messages = state.get("messages", [])
        if messages:
            user_message = messages[-1].get("content", "").lower()
            # Simple heuristic: look for write-related keywords
            write_keywords = ["create", "write", "build", "make", "generate", "modify", "delete", "save"]
            needs_write = any(keyword in user_message for keyword in write_keywords)
            
            state["session"]["is_read_only"] = not needs_write
            state["session"]["is_first_interaction"] = False
            
            # Only announce mode on the very first interaction
            mode_text = f"I'll help you with {'file operations including writing' if needs_write else 'exploring and reading'} files in the workspace directory."
            writer({"custom_llm_chunk": f"\n{mode_text}\n\n"})
            
            logger.info(f"→ determined mode: {'read-write' if needs_write else 'read-only'}")
        else:
            # No messages yet, mark as no longer first but don't set mode
            state["session"]["is_first_interaction"] = False
    
    # Check for repeated actions to prevent infinite loops
    if state["action"]["planned_action"] and state["action"]["action_result"]:
        if state["action"]["action_result"]["success"]:
            action_type = state["action"]["planned_action"]["action_type"]
            action_path = state["action"]["planned_action"]["path"]
            action_key = f"{action_type}:{action_path}"
            
            # Increment counter
            if action_key not in state["action"]["action_counter"]:
                state["action"]["action_counter"][action_key] = 0
            state["action"]["action_counter"][action_key] += 1
            
            # Check if we're repeating too much
            if state["action"]["action_counter"][action_key] >= MAX_ACTION_REPETITIONS:
                logger.info(f"→ detected repeated action: {action_key}, finishing task")
                state["session"]["is_finished"] = True
                
                writer({"custom_llm_chunk": "\nTask completed. Is there anything else you'd like me to help with?\n"})
    
    # Reset planning state for new planning cycle
    state["planning"]["thinking_iterations"] = 0
    state["planning"]["needs_deeper_thinking"] = False
    state["planning"]["current_reasoning"] = ""
    state["planning"]["alternative_approaches"] = []
    
    # Clear previous planned action to ensure fresh planning
    state["action"]["planned_action"] = None
    
    logger.info("→ observation complete, ready for planning")
    
    # Log what this node wrote to state
    log_node_complete("observe", state_before, state)
    return state


