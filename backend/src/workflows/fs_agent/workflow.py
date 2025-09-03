"""
fs_agent LangGraph workflow definition.

This module implements a file system agent workflow that can perform
read and write operations on files in a workspace directory.
"""
import logging
import os
from langgraph.graph import StateGraph, END

from .state import FSAgentState
from .nodes.observe import observe_node
from .nodes.plan import plan_node, should_continue_planning
from .nodes.read_act import read_act_node
from .nodes.write_act import write_act_node
from .nodes.preview import preview_node
from .nodes.human_approve import human_approve_node
from .nodes.utils import is_finished

logger = logging.getLogger(__name__)


def route_after_approval(state: FSAgentState) -> str:
    """
    Route to appropriate action node after approval.
    
    Args:
        state: Current workflow state
        
    Returns:
        "read_act" for read/list operations, "write_act" for write/edit/delete
    """
    planned_action = state["action"]["planned_action"]
    if not planned_action:
        return "read_act"  # Default fallback
    
    action_type = planned_action["action_type"]
    
    if action_type in ["list", "read"]:
        return "read_act"
    elif action_type in ["write", "edit", "delete"]:
        return "write_act"
    else:
        logger.warning(f"Unknown action type: {action_type}, defaulting to read_act")
        return "read_act"


def create_workflow(checkpointer, draw_diagram: bool = False):
    """
    Create the fs_agent LangGraph workflow.
    
    This workflow implements a file system agent following the ReAct pattern:
    
    1. Observe node gathers current state and context
    2. Plan node reasons about next action (with optional think loops)
    3. Safe actions execute directly, risky actions need approval
    4. Preview node generates diffs for risky operations
    5. Human approve node (diamond HITL) collects user approval
    6. Read/Write act nodes execute the planned actions
    7. Action nodes loop back to Observe for next iteration
    
    Flow diagram:
    observe → plan → [safe → read_act/write_act | risky → preview → human_approve → read_act/write_act] → observe (loop) → END
              ↺ think (self-loop, max 2 iterations)
    
    Args:
        checkpointer: LangGraph checkpointer for state persistence
        draw_diagram: Whether to generate workflow diagram
        
    Returns:
        Compiled LangGraph workflow
    """
    logger.info("Creating fs_agent workflow")
    
    # Initialize the graph with our state type
    workflow = StateGraph(FSAgentState)
    
    # Add nodes
    workflow.add_node("observe", observe_node)
    workflow.add_node("plan", plan_node)
    workflow.add_node("preview", preview_node)
    workflow.add_node("human_approve", human_approve_node)
    workflow.add_node("read_act", read_act_node)
    workflow.add_node("write_act", write_act_node)
    
    # Set entry point - start at observe
    workflow.set_entry_point("observe")
    
    # Add edges
    # Observe always goes to plan
    workflow.add_edge("observe", "plan")
    
    # Plan can self-loop (think) or route to safe/risky actions
    workflow.add_conditional_edges(
        "plan",
        should_continue_planning,
        {
            "think": "plan",  # Self-loop for deeper thinking
            "safe": route_after_approval,  # Safe actions execute directly
            "risky": "preview",  # Risky actions need approval
            "none": END
        }
    )
    
    # Approval flow: preview always goes to human_approve
    workflow.add_edge("preview", "human_approve")
    
    # After approval, route to appropriate action node
    workflow.add_conditional_edges(
        "human_approve",
        route_after_approval,
        {
            "read_act": "read_act",
            "write_act": "write_act"
        }
    )
    
    # Action nodes loop back to observe or end
    workflow.add_conditional_edges(
        "read_act",
        is_finished,
        {
            True: END,
            False: "observe"
        }
    )
    
    workflow.add_conditional_edges(
        "write_act",
        is_finished,
        {
            True: END,
            False: "observe"
        }
    )
    
    # Compile the workflow with checkpointer
    compiled = workflow.compile(checkpointer=checkpointer)
    
    # Generate diagram if requested
    if draw_diagram:
        # Generate diagram path in the same directory as this module
        current_dir = os.path.dirname(__file__)
        diagram_path = os.path.join(current_dir, "fs_agent_workflow.png")
        
        logger.info(f"Drawing workflow diagram to {diagram_path}")
        try:
            png_bytes = compiled.get_graph().draw_mermaid_png()
            with open(diagram_path, "wb") as f:
                f.write(png_bytes)
            logger.info(f"Workflow diagram saved successfully to {diagram_path}")
        except Exception as e:
            logger.warning(f"Could not generate workflow diagram: {e}")
    
    logger.info("fs_agent workflow created successfully")
    return compiled