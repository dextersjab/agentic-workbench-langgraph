"""
Base workflow utilities for graph state tracking and workflow introspection.

This module provides common functionality for all LangGraph workflows
including state tracking, graph structure extraction, and utility functions.
"""

import logging
from typing import Dict, Any, Optional

from ..api.graph_state import GraphStructure, update_graph_state

logger = logging.getLogger(__name__)

def extract_graph_structure(workflow) -> GraphStructure:
    """
    Extract the structure of nodes and edges from a LangGraph workflow.
    
    Args:
        workflow: Compiled LangGraph workflow
        
    Returns:
        GraphStructure with nodes and edges information
    """
    try:
        # Get the graph object from the workflow
        graph = workflow.get_graph()
        
        # Extract nodes
        nodes = []
        edges = []
        
        # Get nodes from the graph
        if hasattr(graph, 'nodes'):
            nodes = list(graph.nodes.keys())
        elif hasattr(graph, '_nodes'):
            nodes = list(graph._nodes.keys())
        else:
            # Fallback to common support desk nodes
            nodes = [
                "classify_issue", "clarify_issue", "triage_issue", 
                "has_sufficient_info", "gather_info", "send_to_desk"
            ]
            logger.warning("Could not extract nodes from graph, using default support desk nodes")
        
        # Get edges from the graph  
        if hasattr(graph, 'edges'):
            for edge in graph.edges:
                if hasattr(edge, 'source') and hasattr(edge, 'target'):
                    edges.append({
                        "from": edge.source,
                        "to": edge.target,
                        "condition": getattr(edge, 'condition', None)
                    })
        elif hasattr(graph, '_edges'):
            for source, targets in graph._edges.items():
                if isinstance(targets, list):
                    for target in targets:
                        edges.append({
                            "from": source,
                            "to": target if isinstance(target, str) else str(target)
                        })
                elif isinstance(targets, dict):
                    for condition, target in targets.items():
                        edges.append({
                            "from": source,
                            "to": target if isinstance(target, str) else str(target),
                            "condition": str(condition)
                        })
                else:
                    edges.append({
                        "from": source,
                        "to": targets if isinstance(targets, str) else str(targets)
                    })
        else:
            # Fallback to default support desk edges
            edges = [
                {"from": "classify_issue", "to": "clarify_issue", "condition": "needs_clarification"},
                {"from": "classify_issue", "to": "triage_issue", "condition": "sufficient_info"},
                {"from": "clarify_issue", "to": "classify_issue"},
                {"from": "triage_issue", "to": "has_sufficient_info"},
                {"from": "has_sufficient_info", "to": "gather_info", "condition": "needs_more_info"},
                {"from": "has_sufficient_info", "to": "send_to_desk", "condition": "sufficient_info"},
                {"from": "gather_info", "to": "has_sufficient_info"}
            ]
            logger.warning("Could not extract edges from graph, using default support desk edges")
        
        logger.info(f"Extracted graph structure: {len(nodes)} nodes, {len(edges)} edges")
        return GraphStructure(nodes=nodes, edges=edges)
        
    except Exception as e:
        logger.error(f"Error extracting graph structure: {e}")
        # Return default structure for support desk workflow
        return GraphStructure(
            nodes=["classify_issue", "clarify_issue", "triage_issue", 
                   "has_sufficient_info", "gather_info", "send_to_desk"],
            edges=[
                {"from": "classify_issue", "to": "clarify_issue", "condition": "needs_clarification"},
                {"from": "classify_issue", "to": "triage_issue", "condition": "sufficient_info"},
                {"from": "clarify_issue", "to": "classify_issue"},
                {"from": "triage_issue", "to": "has_sufficient_info"},
                {"from": "has_sufficient_info", "to": "gather_info", "condition": "needs_more_info"},
                {"from": "has_sufficient_info", "to": "send_to_desk", "condition": "sufficient_info"},
                {"from": "gather_info", "to": "has_sufficient_info"}
            ]
        )

def extract_thread_id(state: Dict[str, Any]) -> Optional[str]:
    """
    Extract thread ID/chat ID from workflow state.
    
    Args:
        state: Workflow state dictionary
        
    Returns:
        Thread ID if found, None otherwise
    """
    try:
        # Try different common locations for thread ID
        config = state.get("configurable", {})
        if "thread_id" in config:
            return config["thread_id"]
            
        # Alternative locations
        if "thread_id" in state:
            return state["thread_id"]
            
        if "chat_id" in state:
            return state["chat_id"]
            
        return None
        
    except Exception as e:
        logger.error(f"Error extracting thread ID from state: {e}")
        return None

# Legacy manual tracking function removed - now using automatic stream-based tracking

async def track_node_from_stream(
    node_name: str,
    node_updates: Any,
    config: Dict[str, Any]
) -> None:
    """
    Track node execution from stream updates (new automatic approach).
    
    Args:
        node_name: Name of the executing node
        node_updates: State updates from the node execution (dict, tuple, or other)
        config: Workflow configuration containing thread_id
    """
    try:
        # Extract thread ID from config
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            logger.warning(f"No thread ID found in config for node {node_name}, skipping stream tracking")
            return
        
        # Handle different types of node_updates
        if isinstance(node_updates, dict):
            # Standard dictionary format
            updates_dict = node_updates
        elif isinstance(node_updates, tuple):
            # Handle tuple format - commonly used for interrupts and special data
            logger.debug(f"Stream tracking received tuple for {node_name}: {type(node_updates)}")
            # For tuples, we don't have standard state updates to track
            # Skip tracking for special cases like interrupts
            return
        elif hasattr(node_updates, '__dict__'):
            # Handle objects with attributes
            updates_dict = node_updates.__dict__
        else:
            # Handle other types by converting to string representation
            logger.debug(f"Stream tracking received {type(node_updates)} for {node_name}")
            updates_dict = {"raw_data": str(node_updates)}
        
        # Skip tracking if node_name is a special control key
        if node_name.startswith("__"):
            logger.debug(f"Skipping tracking for control key: {node_name}")
            return
        
        # Filter relevant fields based on node type
        relevant_data = extract_relevant_fields_for_node(node_name, updates_dict)
        
        # Only update if we have relevant data
        if relevant_data:
            # Update graph state
            update_graph_state(thread_id, node_name, relevant_data)
            logger.info(f"Stream tracking: {node_name} -> {relevant_data}")
        else:
            logger.debug(f"No relevant data found for {node_name}, skipping graph state update")
        
    except Exception as e:
        # Log error but don't fail the workflow
        logger.error(f"Failed to track node execution from stream for {node_name}: {e}")

def extract_relevant_fields_for_node(node_name: str, node_updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant fields for tracking based on node type and updates.
    
    Args:
        node_name: Name of the executing node
        node_updates: All state updates from the node
        
    Returns:
        Filtered dictionary with relevant tracking fields
    """
    # Define relevant fields by node name patterns
    field_patterns = {
        "clarify": ["clarification_attempts", "needs_clarification", "current_response"],
        "classify": ["issue_category", "issue_priority", "needs_clarification", "current_response"],
        "triage": ["assigned_team", "issue_category", "issue_priority"],
        "has_sufficient": ["needs_more_info", "info_completeness_confidence", "gathering_round"],
        "gather": ["gathering_round", "needs_more_info", "missing_categories", "current_response"],
        "send_to_desk": ["ticket_id", "ticket_status", "assigned_team", "current_response"]
    }
    
    # Find matching pattern
    relevant_fields = []
    for pattern, fields in field_patterns.items():
        if pattern in node_name.lower():
            relevant_fields = fields
            break
    
    # If no specific pattern found, include common tracking fields
    if not relevant_fields:
        relevant_fields = [
            "needs_clarification", "clarification_attempts", "issue_category", 
            "issue_priority", "gathering_round", "needs_more_info", 
            "info_completeness_confidence", "assigned_team", "ticket_id",
            "current_response"
        ]
    
    # Filter node updates to only include relevant fields
    filtered_data = {}
    for field in relevant_fields:
        if field in node_updates and node_updates[field] is not None:
            filtered_data[field] = node_updates[field]
    
    # Always include any non-private fields that changed if filtered_data is empty
    if not filtered_data:
        filtered_data = {k: v for k, v in node_updates.items() 
                        if not k.startswith("_") and v is not None}
    
    return filtered_data

def create_state_snapshot(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a JSON-serializable snapshot of workflow state.
    
    Args:
        state: Current workflow state
        
    Returns:
        Serializable state snapshot
    """
    try:
        snapshot = {}
        
        # Include only serializable fields
        serializable_fields = [
            "needs_clarification", "clarification_attempts", "max_clarification_attempts",
            "issue_category", "issue_priority", "gathering_round", "max_gathering_rounds",
            "needs_more_info", "info_completeness_confidence", "missing_categories",
            "current_response", "ticket_id", "ticket_status", "assigned_team",
            "sla_commitment", "next_steps", "estimated_resolution_time", "escalation_path"
        ]
        
        for field in serializable_fields:
            if field in state and state[field] is not None:
                # Ensure the value is serializable
                value = state[field]
                if isinstance(value, (str, int, float, bool, list, dict)):
                    snapshot[field] = value
                else:
                    snapshot[field] = str(value)
        
        # Include message count for context
        messages = state.get("messages", [])
        if messages:
            snapshot["message_count"] = len(messages)
            snapshot["last_user_input"] = state.get("current_user_input", "")
        
        return snapshot
        
    except Exception as e:
        logger.error(f"Error creating state snapshot: {e}")
        return {}

def initialize_workflow_tracking(workflow, workflow_name: str = "unknown") -> None:
    """
    Initialize graph state tracking for a workflow.
    
    Args:
        workflow: Compiled LangGraph workflow
        workflow_name: Name of the workflow for logging
    """
    try:
        # Extract and cache the graph structure
        graph_structure = extract_graph_structure(workflow)
        logger.info(f"Initialized state tracking for {workflow_name} workflow")
        logger.info(f"Graph structure: {len(graph_structure.nodes)} nodes, {len(graph_structure.edges)} edges")
        
    except Exception as e:
        logger.error(f"Failed to initialize workflow tracking for {workflow_name}: {e}")

def get_workflow_progress(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate workflow progress metrics from state.
    
    Args:
        state: Current workflow state
        
    Returns:
        Progress metrics dictionary
    """
    try:
        progress = {
            "completion_percentage": 0,
            "current_phase": "initialization",
            "steps_completed": 0,
            "total_steps": 6  # Approximate for support desk workflow
        }
        
        # Determine current phase and completion
        if state.get("ticket_id"):
            progress["completion_percentage"] = 100
            progress["current_phase"] = "completed"
            progress["steps_completed"] = 6
        elif state.get("assigned_team"):
            progress["completion_percentage"] = 85
            progress["current_phase"] = "ticket_creation"
            progress["steps_completed"] = 5
        elif state.get("needs_more_info") is False:
            progress["completion_percentage"] = 70
            progress["current_phase"] = "information_complete"
            progress["steps_completed"] = 4
        elif state.get("issue_category"):
            progress["completion_percentage"] = 50
            progress["current_phase"] = "information_gathering"
            progress["steps_completed"] = 3
        elif state.get("needs_clarification") is False:
            progress["completion_percentage"] = 30
            progress["current_phase"] = "classification"
            progress["steps_completed"] = 2
        else:
            progress["completion_percentage"] = 10
            progress["current_phase"] = "clarification"
            progress["steps_completed"] = 1
        
        return progress
        
    except Exception as e:
        logger.error(f"Error calculating workflow progress: {e}")
        return {
            "completion_percentage": 0,
            "current_phase": "unknown",
            "steps_completed": 0,
            "total_steps": 6
        }