"""
Main HelpHub LangGraph workflow definition.

TODO for participants: Implement the complete LangGraph workflow
connecting all nodes with proper conditional edges.
"""
import logging
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from .state import HelpHubState
from .nodes import (
    clarify_issue_node,
    categorise_issue_node,
    prioritise_issue_node,
    triage_issue_node,
    create_ticket_node
)

logger = logging.getLogger(__name__)


def create_helphub_workflow():
    """
    Create the HelpHub LangGraph workflow.
    
    This workflow implements a linear IT support agent flow:
    __start__ → clarify_issue → categorise_issue → prioritise_issue → triage_issue → create_ticket → __end__
    
    Students will implement each node incrementally:
    1. clarify_issue: Ask clarifying questions for vague issues (IMPLEMENTED)
    2. categorise_issue: Categorize issues (hardware, software, network, access, billing) (TODO)
    3. prioritise_issue: Assess priority based on business impact (P1/P2/P3) (TODO)
    4. triage_issue: Route to appropriate support teams (TODO)
    5. create_ticket: Create ServiceHub tickets automatically (TODO)
    """
    
    logger.info("Creating HelpHub workflow")
    
    # Create the workflow graph
    workflow = StateGraph(HelpHubState)
    
    # Add nodes to the workflow in linear order
    workflow.add_node("clarify_issue", clarify_issue_node)
    workflow.add_node("categorise_issue", categorise_issue_node)
    workflow.add_node("prioritise_issue", prioritise_issue_node)
    workflow.add_node("triage_issue", triage_issue_node)
    workflow.add_node("create_ticket", create_ticket_node)
    
    # Set entry point
    workflow.set_entry_point("clarify_issue")
    
    # Create linear workflow edges
    workflow.add_edge("clarify_issue", "categorise_issue")
    workflow.add_edge("categorise_issue", "prioritise_issue")
    workflow.add_edge("prioritise_issue", "triage_issue")
    workflow.add_edge("triage_issue", "create_ticket")
    workflow.add_edge("create_ticket", END)
    
    # Compile the workflow
    compiled_workflow = workflow.compile()
    
    logger.info("HelpHub workflow compiled successfully")
    return compiled_workflow


def create_advanced_workflow():
    """
    Create an advanced workflow with additional features.
    
    TODO for participants: Implement advanced features like:
    - Multi-turn conversation handling
    - Knowledge base integration
    - Sentiment analysis
    - Auto-resolution attempts
    - Escalation workflows
    - Feedback collection
    """
    
    # TODO: Implement advanced workflow features
    # This is where participants can add:
    # - Knowledge base search nodes
    # - Auto-resolution attempts
    # - Sentiment analysis
    # - Multi-language support
    # - Integration with external systems
    
    logger.info("Advanced workflow not yet implemented")
    return create_helphub_workflow()


def add_human_feedback_loop(workflow):
    """
    Add human-in-the-loop capabilities to the workflow.
    
    TODO for participants:
    - Add interrupt points for human review
    - Implement approval workflows
    - Add quality assurance checkpoints
    - Include customer satisfaction collection
    """
    
    # TODO: Implement human feedback integration
    # Examples:
    # - Add interrupt before ticket creation for P1 issues
    # - Include customer satisfaction survey after resolution
    # - Add quality review for complex categorizations
    # - Implement supervisor approval for escalations
    
    logger.info("Human feedback loop not yet implemented")
    return workflow


def add_monitoring_and_metrics(workflow):
    """
    Add monitoring and metrics collection to the workflow.
    
    TODO for participants:
    - Add performance metrics collection
    - Implement workflow timing analysis
    - Add error tracking and alerting
    - Include business metrics (resolution time, satisfaction)
    """
    
    # TODO: Implement monitoring integration
    # Examples:
    # - Add timing metrics for each node
    # - Track categorization accuracy
    # - Monitor SLA compliance
    # - Collect user satisfaction scores
    # - Alert on workflow failures
    
    logger.info("Monitoring and metrics not yet implemented")
    return workflow
