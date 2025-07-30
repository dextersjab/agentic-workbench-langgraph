"""
Graph State Management for Agentic Workflow Workbench.

This module provides thread-safe in-memory storage and REST API for tracking
workflow execution state, current nodes, and traversal history.
"""

import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from fastapi import APIRouter, HTTPException, status

logger = logging.getLogger(__name__)

@dataclass
class GraphStructure:
    """Represents the structure of a LangGraph workflow."""
    nodes: List[str]
    edges: List[Dict[str, str]]  # [{"from": "node1", "to": "node2", "condition": "optional"}]

@dataclass 
class GraphState:
    """Represents the current state of a workflow execution."""
    chat_id: str
    current_node: Optional[str]
    graph_structure: GraphStructure
    traversal_history: List[str]
    state_data: Dict[str, Any]
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "current_node": self.current_node,
            "graph_structure": {
                "nodes": self.graph_structure.nodes,
                "edges": self.graph_structure.edges
            },
            "traversal_history": self.traversal_history,
            "state_data": self.state_data,
            "last_updated": self.last_updated.isoformat()
        }

class GraphStateManager:
    """Thread-safe manager for workflow state tracking."""
    
    def __init__(self, cleanup_interval_minutes: int = 60):
        self._states: Dict[str, GraphState] = {}
        self._lock = threading.RLock()
        self._cleanup_interval = timedelta(minutes=cleanup_interval_minutes)
        
    def update_graph_state(
        self, 
        chat_id: str, 
        current_node: str, 
        state_data: Dict[str, Any],
        graph_structure: Optional[GraphStructure] = None
    ) -> None:
        """
        Update the workflow state for a given chat.
        
        Args:
            chat_id: Unique identifier for the conversation
            current_node: Name of the currently executing node
            state_data: Current workflow state data
            graph_structure: Graph structure (only needed on first update)
        """
        with self._lock:
            existing_state = self._states.get(chat_id)
            
            if existing_state:
                # Update existing state
                existing_state.current_node = current_node
                existing_state.traversal_history.append(current_node)
                existing_state.state_data.update(state_data)
                existing_state.last_updated = datetime.now()
                logger.info(f"Updated graph state for {chat_id}: {current_node}")
            else:
                # Create new state
                if not graph_structure:
                    # Provide default structure if none given
                    graph_structure = GraphStructure(
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
                
                new_state = GraphState(
                    chat_id=chat_id,
                    current_node=current_node,
                    graph_structure=graph_structure,
                    traversal_history=[current_node],
                    state_data=state_data.copy(),
                    last_updated=datetime.now()
                )
                self._states[chat_id] = new_state
                logger.info(f"Created new graph state for {chat_id}: {current_node}")
    
    def get_graph_state(self, chat_id: str) -> Optional[GraphState]:
        """
        Get the current workflow state for a chat.
        
        Args:
            chat_id: Unique identifier for the conversation
            
        Returns:
            GraphState if found, None otherwise
        """
        with self._lock:
            return self._states.get(chat_id)
    
    def remove_graph_state(self, chat_id: str) -> bool:
        """
        Remove workflow state for a chat.
        
        Args:
            chat_id: Unique identifier for the conversation
            
        Returns:
            True if state was removed, False if not found
        """
        with self._lock:
            if chat_id in self._states:
                del self._states[chat_id]
                logger.info(f"Removed graph state for {chat_id}")
                return True
            return False
    
    def cleanup_old_states(self, max_age_hours: int = 24) -> int:
        """
        Remove old workflow states to free memory.
        
        Args:
            max_age_hours: Maximum age of states to keep
            
        Returns:
            Number of states removed
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        removed_count = 0
        
        with self._lock:
            chat_ids_to_remove = [
                chat_id for chat_id, state in self._states.items()
                if state.last_updated < cutoff_time
            ]
            
            for chat_id in chat_ids_to_remove:
                del self._states[chat_id]
                removed_count += 1
            
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} old graph states")
        
        return removed_count
    
    def get_all_active_chats(self) -> List[str]:
        """Get list of all active chat IDs."""
        with self._lock:
            return list(self._states.keys())

# Global state manager instance
state_manager = GraphStateManager()

# FastAPI router for graph state endpoints
router = APIRouter(prefix="/v1", tags=["graph-state"])

@router.get("/graph-state/{chat_id}")
async def get_graph_state(chat_id: str):
    """
    Get the current workflow state for a specific chat.
    
    Args:
        chat_id: The chat/conversation identifier
        
    Returns:
        JSON object with current node, graph structure, history, and state data
        
    Raises:
        HTTPException: 404 if chat state not found
    """
    try:
        graph_state = state_manager.get_graph_state(chat_id)
        
        if not graph_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No graph state found for chat ID: {chat_id}"
            )
        
        return graph_state.to_dict()
        
    except Exception as e:
        logger.error(f"Error retrieving graph state for {chat_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving graph state: {str(e)}"
        )

@router.get("/graph-state")
async def list_active_chats():
    """
    List all active chat IDs with workflow states.
    
    Returns:
        JSON object with list of active chat IDs
    """
    try:
        active_chats = state_manager.get_all_active_chats()
        return {
            "active_chats": active_chats,
            "count": len(active_chats)
        }
        
    except Exception as e:
        logger.error(f"Error listing active chats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing active chats: {str(e)}"
        )

@router.delete("/graph-state/{chat_id}")
async def delete_graph_state(chat_id: str):
    """
    Delete the workflow state for a specific chat.
    
    Args:
        chat_id: The chat/conversation identifier
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if chat state not found
    """
    try:
        removed = state_manager.remove_graph_state(chat_id)
        
        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No graph state found for chat ID: {chat_id}"
            )
        
        return {"message": f"Graph state for chat {chat_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting graph state for {chat_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting graph state: {str(e)}"
        )

@router.post("/graph-state/cleanup")
async def cleanup_old_states(max_age_hours: int = 24):
    """
    Clean up old workflow states to free memory.
    
    Args:
        max_age_hours: Maximum age of states to keep (default: 24 hours)
        
    Returns:
        Number of states cleaned up
    """
    try:
        removed_count = state_manager.cleanup_old_states(max_age_hours)
        return {
            "message": f"Cleaned up {removed_count} old graph states",
            "removed_count": removed_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up graph states: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cleaning up graph states: {str(e)}"
        )

def update_graph_state(chat_id: str, current_node: str, state_data: Dict[str, Any]) -> None:
    """
    Convenience function for updating graph state from workflow nodes.
    
    Args:
        chat_id: Unique identifier for the conversation  
        current_node: Name of the currently executing node
        state_data: Current workflow state data
    """
    try:
        state_manager.update_graph_state(chat_id, current_node, state_data)
    except Exception as e:
        # Log error but don't fail the workflow
        logger.error(f"Failed to update graph state for {chat_id}: {e}")

def get_graph_state_data(chat_id: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function for getting graph state data.
    
    Args:
        chat_id: Unique identifier for the conversation
        
    Returns:
        Graph state as dictionary or None if not found
    """
    try:
        graph_state = state_manager.get_graph_state(chat_id)
        return graph_state.to_dict() if graph_state else None
    except Exception as e:
        logger.error(f"Failed to get graph state for {chat_id}: {e}")
        return None