"""
fs_agent LangGraph workflow definition.

This module implements a file system agent workflow that can perform
read and write operations on files in a workspace directory.
"""
import logging
from typing import Literal
from langgraph.graph import StateGraph, END

from .state import FSAgentState, create_initial_state
from .nodes.router import router_node, should_route_to_observe
from .nodes.observe import observe_node, determine_action_type
from .nodes.read_act import read_act_node
from .nodes.write_act import write_act_node
from .nodes.utils import is_finished

logger = logging.getLogger(__name__)


def create_workflow(checkpointer, draw_diagram: bool = True):
    """
    Create the fs_agent LangGraph workflow.
    
    This workflow implements a file system agent with the following flow:
    
    1. Router determines if session is read-only or write mode
    2. Observe node plans the next file action based on user request
    3. Read/Write act nodes execute the planned actions
    4. Loop back to observe until task is complete
    
    Flow diagram:
    router → observe → [read_act | write_act] → observe (loop) → END
    
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
    workflow.add_node("router", router_node)
    workflow.add_node("observe", observe_node)
    workflow.add_node("read_act", read_act_node)
    workflow.add_node("write_act", write_act_node)
    
    # Set entry point
    workflow.set_entry_point("router")
    
    # Add edges
    # Router always goes to observe
    workflow.add_edge("router", "observe")
    
    # Observe routes based on action type
    workflow.add_conditional_edges(
        "observe",
        determine_action_type,
        {
            "read": "read_act",
            "write": "write_act",
            "none": END
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
        try:
            png_bytes = compiled.get_graph().draw_mermaid_png()
            diagram_path = "backend/src/workflows/fs_agent/fs_agent_workflow.png"
            with open(diagram_path, "wb") as f:
                f.write(png_bytes)
            logger.info(f"Workflow diagram saved to {diagram_path}")
        except Exception as e:
            logger.warning(f"Could not generate workflow diagram: {e}")
    
    logger.info("fs_agent workflow created successfully")
    return compiled