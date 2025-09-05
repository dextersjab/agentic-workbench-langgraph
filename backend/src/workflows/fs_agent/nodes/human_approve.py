"""
Human Approval node for fs_agent workflow - HITL diamond node.

This node represents the human interaction point for approving risky file operations
after the preview node has generated and streamed the diff/preview.
"""
import logging
from copy import deepcopy

from ..state import FSAgentState
from src.core.state_logger import log_node_start, log_node_complete
from langgraph.types import interrupt

logger = logging.getLogger(__name__)


async def human_approve_node(state: FSAgentState) -> FSAgentState:
    """
    Human interaction node (diamond) that collects user approval for risky operations.
    
    The preview has already been generated and streamed by the preview node.
    This node represents the human touchpoint in the workflow.

    Args:
        state: Workflow global state
    
    Returns:
        Updated state with user's approval decision
    """
    state_before = deepcopy(state)
    
    # Log what this node will read from state
    log_node_start("human_approve", ["approval.needs_approval", "approval.preview_content"], state)
    
    # Check if approval is actually needed
    if not state["approval"]["needs_approval"]:
        logger.info("→ no approval needed, auto-approving")
        state["approval"]["approval_granted"] = True
        
        # Log what this node wrote to state
        log_node_complete("human_approve", state_before, state)
        return state
    
    # Get the planned action for context
    planned_action = state["action"]["planned_action"]
    action_type = planned_action["action_type"] if planned_action else "unknown"
    file_path = planned_action["path"] if planned_action else "unknown"
    
    logger.info(f"→ requesting approval for {action_type} on {file_path}")
    
    # Interrupt and wait for user response (HITL diamond)
    user_response = interrupt(f"Approval needed for {action_type} operation on {file_path}")
    
    # Parse user response
    if user_response:
        response_str = str(user_response).strip().lower()
        
        if response_str in ["yes", "y", "proceed", "ok", "approve", "confirm"]:
            state["approval"]["approval_granted"] = True
            decision = "approved"
            logger.info(f"→ user approved {action_type} on {file_path}")
        elif response_str in ["no", "n", "cancel", "abort", "reject", "deny"]:
            state["approval"]["approval_granted"] = False
            decision = "rejected"
            logger.info(f"→ user rejected {action_type} on {file_path}")
        else:
            # Unclear response, default to rejection for safety
            state["approval"]["approval_granted"] = False
            decision = "unclear (defaulted to rejected)"
            logger.info(f"→ unclear response '{response_str}', defaulting to rejection")
    else:
        # No response, default to rejection for safety
        state["approval"]["approval_granted"] = False
        decision = "no response (defaulted to rejected)"
        logger.info("→ no response received, defaulting to rejection")
    
    # Add approval decision to messages for context
    if "messages" not in state:
        state["messages"] = []
    
    approval_message = {
        "role": "user",
        "content": f"Approval decision: {decision}"
    }
    state["messages"].append(approval_message)
    
    logger.info(f"→ approval decision: {decision}")
    
    # Log what this node wrote to state
    log_node_complete("human_approve", state_before, state)
    
    return state