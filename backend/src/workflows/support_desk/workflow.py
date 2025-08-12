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
from .nodes.human_clarification import human_clarification_node
from .nodes.classify_issue import classify_issue_node, should_continue_to_triage
from .nodes.triage_issue import triage_issue_node
from .nodes.has_sufficient_info import has_sufficient_info_node, has_sufficient_info
from .nodes.gather_info import gather_info_node
from .nodes.send_to_desk import send_to_desk_node

logger = logging.getLogger(__name__)


# Removed separate clarification routing function - using should_continue_clarifying from node


def create_workflow(checkpointer, draw_diagram: bool = True):
    """
    Create the Support Desk LangGraph workflow with classify-first and iterative gathering.
    
    This workflow implements an IT support agent flow with natural conversation and HITL:
    
    Enhanced Flow with Info Sufficiency Check:
    classify_issue → [sufficient info?] → triage_issue → has_sufficient_info
         ↑               [no]                                ↓ [False]        ↓ [True]
         └─── human_clarification ←──┘              gather_info ←──┘    send_to_desk
                                                           ↓ [asked question]
                                                      has_sufficient_info
    
    Natural Flow Behavior:
    - classify_issue attempts classification first
    - If insufficient information: routes to human_clarification for questions  
    - human_clarification collects user details and returns to classification
    - triage_issue assigns support team once classification is confident
    - has_sufficient_info determines if enough info exists (fast tool call)
    - gather_info asks ONE targeted question using streaming (HITL)
    - Loop: user responds → has_sufficient_info → gather_info (max 3 rounds)
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
    workflow.add_node("human_clarification", human_clarification_node)
    workflow.add_node("classify_issue", classify_issue_node)
    workflow.add_node("triage_issue", triage_issue_node)
    workflow.add_node("has_sufficient_info", has_sufficient_info_node)
    workflow.add_node("gather_info", gather_info_node)
    workflow.add_node("send_to_desk", send_to_desk_node)
    
    # Set entry point to classification
    workflow.set_entry_point("classify_issue")
    
    # Conditional edge from classification: clarify, triage, or escalate
    workflow.add_conditional_edges(
        "classify_issue",
        should_continue_to_triage,
        {
            "clarify": "human_clarification",    # Need clarification - question generated in classify
            "triage": "triage_issue",       # Ready to proceed with triage
            "escalate": "send_to_desk"      # User requested escalation
        }
    )
    
    # Human clarification loops back to classification
    workflow.add_edge("human_clarification", "classify_issue")
    
    # Continue with info sufficiency check after triage
    workflow.add_edge("triage_issue", "has_sufficient_info")
    
    # Conditional edge from info check: either create ticket or gather more info
    workflow.add_conditional_edges(
        "has_sufficient_info",
        has_sufficient_info,
        {
            True: "send_to_desk",          # Sufficient info - create ticket
            False: "gather_info"           # Need more information
        }
    )
    
    # After asking a question, check sufficiency again
    workflow.add_edge("gather_info", "has_sufficient_info")
    
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