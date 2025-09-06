"""
Support Desk LangGraph workflow definition with conditional loop logic.

This module implements the IT Support Desk workflow with a conditional
clarification loop, demonstrating advanced LangGraph patterns.
"""

import logging
import os
from langgraph.graph import StateGraph, END

from .state import SupportDeskState
from .nodes.human_clarification import human_clarification_node
from .nodes.classify_issue import classify_issue_node, should_continue_to_route
from .nodes.route_issue import route_issue_node
from .nodes.assess_info import assess_info_node, should_continue_to_send
from .nodes.human_information import human_information_node
from .nodes.send_to_desk import send_to_desk_node

logger = logging.getLogger(__name__)


# Removed separate clarification routing function - using should_continue_clarifying from node


def create_workflow(checkpointer, draw_diagram: bool = False):
    """
    Create the Support Desk LangGraph workflow with classify-first and iterative gathering.

    This workflow implements an IT support agent flow with natural conversation and HITL:

    Enhanced Flow with Info Assessment:
    classify_issue → [sufficient info?] → route_issue → assess_info
         ↑               [no]                                ↓ [clarify]    ↓ [proceed/escalate]
         └─── human_clarification ←──┘      human_information ←──┘    send_to_desk
                                                           ↓ [collected response]
                                                      assess_info

    Natural Flow Behavior:
    - classify_issue attempts classification first
    - If insufficient information: routes to human_clarification for questions
    - human_clarification collects user details and returns to classification
    - route_issue assigns support team once classification is confident
    - assess_info determines if enough info exists and generates questions when needed
    - human_information collects user responses (HITL)
    - Loop: user responds → assess_info → human_information (max 3 rounds)
    - send_to_desk creates comprehensive ticket once information is complete

    This approach provides natural conversation rhythm with human-in-the-loop interactions
    at key decision points, avoiding overwhelming walls of text.

    Args:
        checkpointer: The checkpointer to use for persisting graph state.
        draw_diagram: Whether to draw and save a mermaid diagram of the workflow.

    Returns:
        A compiled LangGraph workflow
    """

    logger.info("Creating Support Desk workflow")

    # Create the workflow graph
    workflow = StateGraph(SupportDeskState)

    # Add nodes to the workflow
    workflow.add_node("classify_issue", classify_issue_node)
    workflow.add_node("human_clarification", human_clarification_node)
    workflow.add_node("route_issue", route_issue_node)
    workflow.add_node("assess_info", assess_info_node)
    workflow.add_node("human_information", human_information_node)
    workflow.add_node("send_to_desk", send_to_desk_node)

    # Set entry point to classification
    workflow.set_entry_point("classify_issue")

    # Conditional edge from classification: clarify, proceed, or escalate
    workflow.add_conditional_edges(
        "classify_issue",
        should_continue_to_route,
        {
            "proceed": "route_issue",  # Classification complete - proceed to routing
            "clarify": "human_clarification",  # Need clarification - question generated in classify
            "escalate": "send_to_desk",  # User requested escalation
        },
    )

    # Human clarification loops back to classification
    workflow.add_edge("human_clarification", "classify_issue")

    # Continue with info assessment after routing
    workflow.add_edge("route_issue", "assess_info")

    # Conditional edge from info assessment: proceed, clarify, or escalate
    workflow.add_conditional_edges(
        "assess_info",
        should_continue_to_send,
        {
            "proceed": "send_to_desk",  # Assessment complete - proceed to send
            "clarify": "human_information",  # Need more information - question generated in assess
            "escalate": "send_to_desk",  # User requested escalation - force proceed
        },
    )

    # After collecting user response, assess info again
    workflow.add_edge("human_information", "assess_info")

    workflow.add_edge("send_to_desk", END)

    # Compile the workflow with the provided checkpointer
    compiled_workflow = workflow.compile(checkpointer=checkpointer)

    # Generate mermaid diagram if requested
    if draw_diagram:
        # Generate diagram path in the same directory as this module
        current_dir = os.path.dirname(__file__)
        diagram_path = os.path.join(current_dir, "support_desk_workflow.png")

        logger.info(f"Drawing workflow diagram to {diagram_path}")
        try:
            png_bytes = compiled_workflow.get_graph().draw_mermaid_png()
            with open(diagram_path, "wb") as f:
                f.write(png_bytes)
            logger.info(f"Workflow diagram saved successfully to {diagram_path}")
            mermaid_diagram = compiled_workflow.get_graph().draw_mermaid()
            logger.info(mermaid_diagram)
        except Exception as e:
            logger.warning(f"Failed to generate workflow diagram: {e}")

    logger.info("Support Desk workflow compiled successfully")
    return compiled_workflow
