"""Utilities for Support Desk workflow."""
from .conversation import build_conversation_history, truncate_conversation_if_needed

__all__ = ["build_conversation_history", "truncate_conversation_if_needed"]