"""
Main entry point for the LangGraph application.

This module exposes the compiled graph for the support desk workflow.
"""
from my_workflows.support_desk.workflow import create_workflow

# Create and compile the support desk workflow
# Note: LangGraph Platform handles persistence automatically, no custom checkpointer needed
support_desk_graph = create_workflow(checkpointer=None, draw_diagram=False)

# Expose the compiled graph for LangGraph Platform
graph = support_desk_graph