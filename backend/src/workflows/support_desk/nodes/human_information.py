"""
Human Information node for Support Desk workflow - HITL diamond node.

This node represents the human interaction point for collecting additional information
after assess_info has generated and streamed the information gathering question.
"""
import logging
from copy import deepcopy

from ..state import SupportDeskState
from src.core.state_logger import log_node_start, log_node_complete
from langgraph.types import interrupt

logger = logging.getLogger(__name__)


async def human_information_node(state: SupportDeskState) -> SupportDeskState:
    """
    Human interaction node (diamond) that collects additional information.
    
    The information gathering question has already been generated and streamed by assess_info.
    This node represents the human touchpoint in the workflow.

    Args:
        state: Workflow global state
    
    Returns:
        Updated state with user's information response
    """
    state_before = deepcopy(state)
    
    # Log what this node will read from state
    log_node_start("human_information", ["messages", "gathering.gathering_round"])
    
    # Get current gathering round
    gathering_round = state.get("gathering", {}).get("gathering_round", 1)
    
    # Interrupt and wait for user response (HITL diamond)
    user_response = interrupt("Waiting for user response to information gathering")
    
    # Add user response to messages
    if user_response and str(user_response).strip():
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append({
            "role": "user",
            "content": str(user_response)
        })
        logger.info(f"→ received user response: {str(user_response)[:50]}...")
    
    # Increment gathering round
    if "gathering" not in state:
        state["gathering"] = {}
    state["gathering"]["gathering_round"] = gathering_round + 1
    logger.info(f"→ gathering round {gathering_round + 1} complete")
    
    # Log what this node wrote to state
    log_node_complete("human_information", state_before, state)
    
    return state