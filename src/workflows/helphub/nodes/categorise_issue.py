"""
Categorise Issue node for HelpHub workflow.

TODO for students: Implement issue categorization logic.
"""
import logging
from typing import Dict, Any
from ..state import HelpHubState

logger = logging.getLogger(__name__)


def categorise_issue_node(state: HelpHubState) -> Dict[str, Any]:
    """
    Categorize the IT issue into one of the predefined categories.
    
    TODO for students: Implement this node to:
    1. Analyze the user's issue description
    2. Categorize into: hardware, software, network, access, billing
    3. Set appropriate confidence levels
    4. Update the workflow state with category information
    
    Categories:
    - hardware: Physical device issues (laptop, printer, phone, etc.)
    - software: Application problems, installation issues, crashes
    - network: WiFi, VPN, internet connectivity issues
    - access: Login problems, permissions, account issues
    - billing: License requests, cost queries, subscription issues
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with category information
    """
    
    logger.info("Categorise issue node - passing through (TODO: implement categorization)")
    
    # TODO: Students will implement:
    # 1. LLM-based categorization using prompts
    # 2. Confidence scoring for categories
    # 3. Multi-category issue handling
    # 4. Category-specific follow-up questions
    
    # Pass-through implementation - just continue to next node
    user_input = state.get("current_user_input", "")
    response = f"I'm analyzing your issue: '{user_input}'. Moving to priority assessment..."
    
    state["current_response"] = response
    state["custom_llm_chunk"] = response
    
    # Placeholder category - students will implement proper categorization
    state["category"] = "unknown"
    state["category_confidence"] = 0.5
    
    return state