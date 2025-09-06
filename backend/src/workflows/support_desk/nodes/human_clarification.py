"""
Human Clarification node for Support Desk workflow - HITL diamond node.

This node represents the human interaction point for collecting user clarifications
after classify_issue has generated and streamed the clarifying question.
"""

import logging
from copy import deepcopy

from ..state import SupportDeskState
from src.core.state_logger import log_node_start, log_node_complete
from langgraph.types import interrupt

logger = logging.getLogger(__name__)


async def human_clarification_node(state: SupportDeskState) -> SupportDeskState:
    """
    Human interaction node (diamond) that collects user clarification.

    The clarifying question has already been generated and streamed by classify_issue.
    This node represents the human touchpoint in the workflow.

    Args:
        state: Workflow global state

    Returns:
        Updated state with user's clarification response
    """
    state_before = deepcopy(state)

    # Log what this node will read from state
    log_node_start(
        "human_clarification", ["messages", "gathering.clarification_attempts"]
    )

    # Get current clarification attempts
    clarification_attempts = state.get("gathering", {}).get("clarification_attempts", 0)

    # Interrupt and wait for user response (HITL diamond)
    user_response = interrupt("Waiting for user response to clarification")

    # Add user response to messages
    if user_response and str(user_response).strip():
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append({"role": "user", "content": str(user_response)})
        logger.info(f"→ received user response: {str(user_response)[:50]}...")

    # Increment clarification attempts
    if "gathering" not in state:
        state["gathering"] = {}
    state["gathering"]["clarification_attempts"] = clarification_attempts + 1
    logger.info(f"→ clarification attempt {clarification_attempts + 1} complete")

    # Log what this node wrote to state
    log_node_complete("human_clarification", state_before, state)

    return state
