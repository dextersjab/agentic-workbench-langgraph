"""
Utility functions for Support Desk workflow.

This module contains shared utilities used across multiple nodes.
"""
from typing import List, Dict, Any, Optional


def build_conversation_history(messages: List[Dict[str, Any]], last_n_messages: Optional[int] = None) -> str:
    """
    Build a formatted conversation history string from messages.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        last_n_messages: Optional limit to only include the last N messages
        
    Returns:
        Formatted conversation history string
    """
    if not messages:
        return ""
    
    # Limit to last N messages if specified
    if last_n_messages is not None:
        messages = messages[-last_n_messages:]
    
    # Build conversation history
    conversation_history = "\n".join([
        f"{msg.get('role', 'user')}: {msg.get('content', '')}" 
        for msg in messages
    ])
    
    return conversation_history 