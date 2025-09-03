"""
Utility for loading Support Desk ontologies from JSON files.
"""
import json
from pathlib import Path
from typing import Dict, Any, Tuple


def load_ontologies() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """
    Load all ontologies from JSON files.
    
    Returns:
        Tuple of (categories, priorities, required_info) dictionaries
    """
    base_path = Path(__file__).parent.parent
    ontologies_path = base_path / "ontologies"
    
    # Load categories
    with open(ontologies_path / "categories_ontology.json", "r") as f:
        categories = json.load(f)
    
    # Load priorities  
    with open(ontologies_path / "priority_ontology.json", "r") as f:
        priorities = json.load(f)
        
    # Load required information
    with open(ontologies_path / "required_information_ontology.json", "r") as f:
        required_info = json.load(f)
    
    return categories, priorities, required_info


def format_categories_for_prompt(categories: Dict[str, Any]) -> str:
    """Format category ontology for injection into prompt."""
    formatted = []
    for key, cat in categories["issue_categories"].items():
        formatted.append(f"{cat['name']}: {cat['description']}")
    return "\n".join(formatted)


def format_priorities_for_prompt(priorities: Dict[str, Any]) -> str:
    """Format priority ontology for injection into prompt."""
    formatted = []
    for key, pri in priorities["priority_levels"].items():
        formatted.append(f"- {pri['name']}: {pri['description']}")
    return "\n".join(formatted)


def format_required_info_for_prompt(required_info: Dict[str, Any]) -> str:
    """Format required information categories for injection into prompt."""
    formatted = []
    for cat_id, cat_info in required_info["required_information_categories"].items():
        formatted.append(f"- **{cat_info['name']}**: {cat_info['description']}")
    return "\n".join(formatted)


def get_category_priorities(required_info: Dict[str, Any], issue_category: str) -> str:
    """Get priority information categories for a specific issue category."""
    if issue_category and issue_category.lower() in required_info["category_specific_priorities"]:
        priority_ids = required_info["category_specific_priorities"][issue_category.lower()]
        priorities = []
        for pid in priority_ids:
            if pid in required_info["required_information_categories"]:
                cat_info = required_info["required_information_categories"][pid]
                priorities.append(f"- {cat_info['name']}: {cat_info['description']}")
        return "\n".join(priorities)
    return "- All information categories are equally important"


def get_sla_commitment(priorities: Dict[str, Any], priority: str) -> tuple[str, int]:
    """
    Get SLA commitment for support desk based on priority ontology.
    
    Args:
        priorities: Priority ontology dictionary
        priority: Issue priority (P1, P2, P3, P4)
        
    Returns:
        Tuple of (SLA description, hours)
    """
    priority_key = priority.lower() if priority else "p3"
    
    if priority_key not in priorities["priority_levels"]:
        priority_key = "p3"  # Default to medium priority
    
    priority_info = priorities["priority_levels"][priority_key]
    base_hours = priority_info["resolution_hours"]
    multiplier = priority_info["multiplier"]
    
    # Apply business hours multiplier for non-critical issues
    if priority_key != "p1":
        adjusted_hours = int(base_hours * multiplier / 2.0)  # Normalize multiplier
    else:
        adjusted_hours = base_hours  # Critical issues get full 24/7 commitment
    
    return (f"{adjusted_hours} hours", adjusted_hours)