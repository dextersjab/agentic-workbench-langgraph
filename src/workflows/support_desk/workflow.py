"""
Support Desk LangGraph workflow definition with conditional loop logic.

This module implements the IT Support Desk workflow with a conditional
clarification loop, demonstrating advanced LangGraph patterns.
"""
import logging
import os
from typing import Literal
from langgraph.graph import StateGraph, END

from .state import SupportDeskState
from .nodes.clarify_issue import clarify_issue_node
from .nodes.classify_issue import classify_issue_node
from .nodes.triage_issue import triage_issue_node
from .nodes.gather_info import gather_info_node
from .nodes.send_to_desk import send_to_desk_node

logger = logging.getLogger(__name__)


def should_continue_clarifying(state: SupportDeskState) -> Literal["clarify", "classify"]:
    """
    Predicate function for conditional edge from clarify_issue node.
    
    This function determines whether to:
    1. Loop back to clarify_issue for more information (when needs_clarification=True)
    2. Proceed to classify_issue when we have enough information (needs_clarification=False)
    
    Args:
        state: Current workflow state
        
    Returns:
        "clarify" to loop back for more clarification
        "classify" to proceed to classification
    """
    if state.get("needs_clarification", False):
        logger.info("Need more clarification, looping back to clarify_issue")
        return "clarify"
    else:
        logger.info("Have enough information, proceeding to classify_issue")
        return "classify"


def create_workflow(draw_diagram: bool = True):
    """
    Create the Support Desk LangGraph workflow with conditional loop.
    
    This workflow implements an IT support agent flow with a conditional clarification loop:
    
    Phase 1 (Linear Flow):
    clarify_issue → classify_issue → triage_issue → gather_info → send_to_desk
    
    Phase 2 (Conditional Loop):
    clarify_issue ⟲ (stays in clarify until clear) → classify_issue → triage_issue → gather_info → send_to_desk
    
    The conditional loop demonstrates how to implement stateful, multi-turn conversations
    that can adapt based on the quality and completeness of user input.
    
    Args:
        draw_diagram: Whether to draw and save a mermaid diagram of the workflow.
    
    Returns:
        A compiled LangGraph workflow
    """
    
    logger.info("Creating Support Desk workflow")
    
    # Create the workflow graph
    workflow = StateGraph(SupportDeskState)
    
    # Add nodes to the workflow
    workflow.add_node("clarify_issue", clarify_issue_node)
    workflow.add_node("classify_issue", classify_issue_node)
    workflow.add_node("triage_issue", triage_issue_node)
    workflow.add_node("gather_info", gather_info_node)
    workflow.add_node("send_to_desk", send_to_desk_node)
    
    # Set entry point
    workflow.set_entry_point("clarify_issue")
    
    # Add conditional edge for clarification loop
    workflow.add_conditional_edges(
        "clarify_issue",
        should_continue_clarifying,
        {
            "clarify": "clarify_issue",  # Loop back to clarify
            "classify": "classify_issue"  # Proceed to classification
        }
    )
    
    # Add remaining edges for linear flow
    workflow.add_edge("classify_issue", "triage_issue")
    workflow.add_edge("triage_issue", "gather_info")
    workflow.add_edge("gather_info", "send_to_desk")
    workflow.add_edge("send_to_desk", END)
    
    # Compile the workflow
    compiled_workflow = workflow.compile()
    
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