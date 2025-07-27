"""
Support Desk LangGraph workflow definition with conditional loop logic.

This module implements the IT Support Desk workflow with a conditional
clarification loop, demonstrating advanced LangGraph patterns.
"""
import logging
import os
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import SupportDeskState
from .nodes.clarify_issue import clarify_issue_node, should_continue_to_triage
from .nodes.classify_issue import classify_issue_node
from .nodes.triage_issue import triage_issue_node
from .nodes.gather_info import gather_info_node
from .nodes.send_to_desk import send_to_desk_node

logger = logging.getLogger(__name__)


# Removed separate clarification routing function - using should_continue_clarifying from node


def create_workflow(checkpointer, draw_diagram: bool = True):
    """
    Create the Support Desk LangGraph workflow with classify-first approach.
    
    This workflow implements an IT support agent flow with natural conversation flow:
    
    Classify-First Flow:
    classify_issue → [sufficient info?] → triage_issue → gather_info → send_to_desk
         ↑               [no]
         └─── clarify_issue ←──┘
    
    Natural Flow Behavior:
    - classify_issue attempts classification first
    - If insufficient information: routes to clarify_issue for questions
    - clarify_issue asks for details and returns to classification
    - Loops until sufficient information is gathered
    - No interrupt() calls needed - just natural conditional flow
    
    This approach provides a more intuitive user experience by attempting to help
    immediately and falling back to clarification only when necessary.
    
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
    workflow.add_node("clarify_issue", clarify_issue_node)
    workflow.add_node("classify_issue", classify_issue_node)
    workflow.add_node("triage_issue", triage_issue_node)
    workflow.add_node("gather_info", gather_info_node)
    workflow.add_node("send_to_desk", send_to_desk_node)
    
    # Set entry point to classification
    workflow.set_entry_point("classify_issue")
    
    # Conditional edge from classification: either proceed or ask for clarification
    workflow.add_conditional_edges(
        "classify_issue",
        should_continue_to_triage,
        {
            False: "clarify_issue",    # Need clarification
            True: "triage_issue"       # Ready to proceed
        }
    )
    
    # Clarification loops back to classification
    workflow.add_edge("clarify_issue", "classify_issue")
    
    # Continue with remaining linear flow
    workflow.add_edge("triage_issue", "gather_info")
    workflow.add_edge("gather_info", "send_to_desk")
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