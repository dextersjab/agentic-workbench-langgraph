"""
Route Issue node for Support Desk workflow.

This node routes the issue to the appropriate support team using deterministic rules.
"""

import logging
from copy import deepcopy

from ..state import SupportDeskState, update_state_from_output
from ..models.route_output import RouteOutput
from ..business_context import get_routing_decision
from ..utils import build_conversation_history
from src.core.state_logger import log_node_start, log_node_complete

logger = logging.getLogger(__name__)


async def route_issue_node(state: SupportDeskState) -> SupportDeskState:
    """
    Route the issue to the appropriate support team using deterministic rules.

    This node uses business rules and lookup tables to determine routing
    based on issue category, priority, and conversation content.

    Args:
        state: Current workflow state

    Returns:
        Updated state with routing and team assignment information
    """

    state_before = deepcopy(state)

    # Log what this node will read from state
    log_node_start("route_issue", ["issue_category", "issue_priority", "messages"])

    # Extract relevant information from nested state
    issue_category = state.get("classification", {}).get("issue_category", "other")
    issue_priority = state.get("classification", {}).get("issue_priority", "P2")
    messages = state.get("conversation", {}).get("messages", [])

    # Build conversation history for keyword analysis
    conversation_history = build_conversation_history(messages)

    try:
        # Get deterministic routing decision based on business rules
        routing_decision = get_routing_decision(
            issue_category=issue_category,
            issue_priority=issue_priority,
            conversation_text=conversation_history,
        )

        # Create RouteOutput from the decision
        route_output = RouteOutput(
            support_team=routing_decision["support_team"],
            estimated_resolution_time=routing_decision["estimated_resolution_time"],
            escalation_path=routing_decision["escalation_path"],
        )

        logger.info(
            f"→ {route_output.support_team} team ({route_output.estimated_resolution_time})"
        )

        # DON'T stream - this is internal processing, not user-facing
        # Routing happens silently and routes to assess_info

        # Update state with structured routing information using helper
        update_state_from_output(
            state,
            route_output,
            {
                "support_team": "assigned_team",
                "estimated_resolution_time": "estimated_resolution_time",
                "escalation_path": "escalation_path",
            },
        )

        # DON'T add to conversation history - this is internal routing
        # The user doesn't need to see "Your issue has been assigned to L1..."

        logger.info("→ routing complete")

    except Exception as e:
        logger.error(f"Error in route_issue_node: {e}")
        # Don't mask the real error with fallback messages
        # Let the error propagate for clean error handling
        raise

    # Log what this node wrote to state
    log_node_complete("route_issue", state_before, state)

    return state
