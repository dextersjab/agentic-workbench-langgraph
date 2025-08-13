"""
Human Gather Info node for Support Desk workflow - HITL diamond node.

This node represents the human interaction point for collecting additional information
after assess_info has generated and streamed the gathering question.
"""
import logging
from copy import deepcopy

from ..state import SupportDeskState
from langgraph.types import interrupt

logger = logging.getLogger(__name__)


async def human_gather_info_node(state: SupportDeskState) -> SupportDeskState:
    """
    Human interaction node (diamond) that collects additional information.
    
    The information gathering question has already been generated and streamed by assess_info.
    This node represents the human touchpoint in the workflow.

    Args:
        state: Workflow global state
    
    Returns:
        Updated state with user's information response
    """
    state = deepcopy(state)
    
    # Log node entry
    logger.info("→ human_gather_info: waiting for user response")
    
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
    
    return state