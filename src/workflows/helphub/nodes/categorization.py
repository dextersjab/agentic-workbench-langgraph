"""
Categorization node for HelpHub workflow.

TODO for participants: Implement intelligent ticket categorization using LLM
with knowledge base context and conversation history.
"""
import logging
from typing import Dict, Any
from ..state import HelpHubState
from ..prompts.categorization_prompt import CATEGORIZATION_PROMPT

logger = logging.getLogger(__name__)


def categorization_node(state: HelpHubState) -> Dict[str, Any]:
    """
    Categorize the IT support issue into appropriate category.
    
    This node should:
    1. Use the conversation history and user input
    2. Reference knowledge base articles for context
    3. Determine the most appropriate category: hardware, software, network, access, billing
    4. Provide confidence score for the categorization
    5. Handle edge cases and multi-category issues
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with ticket category
        
    TODO for participants:
    - Implement LLM call using CATEGORIZATION_PROMPT
    - Parse conversation history for context
    - Use KB articles to inform categorization decisions
    - Handle cases where multiple categories might apply
    - Set appropriate confidence levels
    - Consider user context (role, department) in categorization
    """
    
    logger.info("Categorization node processing issue")
    
    user_input = state.get("current_user_input", "")
    conversation_history = state.get("messages", [])
    kb_articles = state.get("kb_articles", [])
    
    # TODO: Replace this placeholder with LLM-based categorization
    # You should:
    # 1. Use CATEGORIZATION_PROMPT to structure the analysis
    # 2. Include conversation history and KB context in the prompt
    # 3. Call LLM to determine category: hardware, software, network, access, billing
    # 4. Parse LLM response to extract category and confidence level
    # 5. Handle edge cases and multi-category issues
    
    # Placeholder logic - participants should implement LLM-based categorization
    category = "software"  # Default category for now
    confidence = 0.85
    
    # Update state
    state["ticket_category"] = category
    
    # Log the categorization
    logger.info(f"Categorized as: {category} (confidence: {confidence})")
    
    # Set response for streaming
    response = f"I've analyzed your request and categorized this as a {category} issue."
    state["current_response"] = response
    state["custom_llm_chunk"] = response
    
    return state


def handle_multi_category_issues(state: HelpHubState) -> Dict[str, Any]:
    """
    Handle cases where the issue spans multiple categories.
    
    TODO for participants:
    - Implement logic to detect multi-category issues
    - Prioritize which issue to handle first
    - Store additional issues for later processing
    - Communicate the handling plan to the user
    """
    
    # TODO: Implement multi-category detection and handling
    # For now, proceed with single category
    return state