"""
Conversation utility functions for Support Desk workflow.

This module contains utilities for building and formatting conversation history.
"""

from typing import List, Dict, Any


def truncate_conversation_if_needed(
    messages: List[Dict[str, Any]],
    max_length: int = 5000,
    keep_start: int = 5,
    keep_end: int = 5,
) -> List[Dict[str, Any]]:
    """
    Truncate conversation history if it's too long, keeping start and end messages.

    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        max_length: Maximum total character length of conversation content
        keep_start: Number of messages to keep from the beginning
        keep_end: Number of messages to keep from the end

    Returns:
        Truncated list of messages with summary message inserted if truncation occurred
    """
    if not messages:
        return messages

    # Calculate total length
    total_length = sum(len(msg.get("content", "")) for msg in messages)

    # If within limit, return as-is
    if total_length <= max_length:
        return messages

    # If we have fewer messages than we want to keep, return all
    if len(messages) <= (keep_start + keep_end):
        return messages

    # Get start and end messages
    start_messages = messages[:keep_start]
    end_messages = messages[-keep_end:]

    # Count truncated messages
    truncated_count = len(messages) - keep_start - keep_end

    # Create truncation summary message
    truncation_summary = {
        "role": "system",
        "content": f"[... {truncated_count} messages truncated to keep conversation manageable ...]",
    }

    # Combine start + summary + end
    return start_messages + [truncation_summary] + end_messages


def build_conversation_history(messages: List[Dict[str, Any]]) -> str:
    """
    Build a formatted conversation history string from messages.

    Args:
        messages: List of message dictionaries with 'role' and 'content' keys

    Returns:
        Formatted conversation history string
    """
    if not messages:
        return ""

    # Truncate if conversation is too long
    messages = truncate_conversation_if_needed(messages)

    # Build conversation history
    conversation_history = "\n".join(
        [f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in messages]
    )

    return conversation_history
