"""Utilities for Support Desk workflow."""
from .conversation import build_conversation_history, truncate_conversation_if_needed
from .ontology_loader import (
    load_ontologies,
    format_categories_for_prompt,
    format_priorities_for_prompt,
    format_required_info_for_prompt,
    get_category_priorities,
    get_sla_commitment
)

__all__ = [
    "build_conversation_history", 
    "truncate_conversation_if_needed",
    "load_ontologies",
    "format_categories_for_prompt",
    "format_priorities_for_prompt",
    "format_required_info_for_prompt",
    "get_category_priorities",
    "get_sla_commitment"
]