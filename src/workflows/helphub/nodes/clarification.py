"""
Clarification node for HelpHub workflow.

TODO for participants: Implement the logic to determine when clarification is needed
and generate appropriate questions to gather more information from users.
"""
import logging
from typing import Dict, Any
from ..state import HelpHubState
from ..prompts.clarification_prompt import CLARIFICATION_PROMPT, ANALYSIS_PROMPT

logger = logging.getLogger(__name__)


def clarification_node(state: HelpHubState) -> Dict[str, Any]:
    """
    Analyze user input and determine if clarification is needed.
    
    This node should:
    1. Analyze the user's input for clarity and completeness
    2. Determine if enough information exists to categorize the issue
    3. Generate clarifying questions if needed
    4. Update the conversation state appropriately
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with clarification decision and any questions
        
    TODO for participants:
    - Implement LLM call to analyze user input clarity
    - Create logic to determine when clarification is sufficient
    - Generate contextually appropriate clarifying questions
    - Handle the case where max clarification attempts are reached
    - Consider different clarification strategies for different issue types
    """
    
    logger.info("Clarification node processing user input")
    
    user_input = state.get("current_user_input", "")
    clarification_attempts = state.get("clarification_attempts", 0)
    max_attempts = state.get("max_clarification_attempts", 3)
    
    # TODO: Replace this placeholder logic with LLM-based analysis
    # You should use the ANALYSIS_PROMPT to determine if the input is clear enough
    
    # Placeholder logic - participants should replace this
    if len(user_input.split()) < 3 and clarification_attempts < max_attempts:
        # Input seems too vague
        needs_clarification = True
        
        # TODO: Use CLARIFICATION_PROMPT to generate better questions
        clarifying_question = "Can you provide more details about the issue you're experiencing?"
        
        state["needs_clarification"] = True
        state["clarification_attempts"] = clarification_attempts + 1
        state["current_response"] = clarifying_question
        state["custom_llm_chunk"] = clarifying_question
        
        logger.info(f"Requesting clarification (attempt {clarification_attempts + 1})")
        
    else:
        # Either input is clear enough OR max attempts reached
        state["needs_clarification"] = False
        
        if clarification_attempts >= max_attempts:
            # Proceed with best guess
            state["current_response"] = "I'll proceed with the information provided."
            state["custom_llm_chunk"] = "I'll proceed with the information provided."
            logger.info("Max clarification attempts reached, proceeding")
        else:
            logger.info("Input appears clear enough, proceeding to categorization")
    
    return state


def should_continue_clarification(state: HelpHubState) -> str:
    """
    Determine the next step after clarification.
    
    Returns:
        "continue_clarification" if more questions needed
        "categorization" if ready to categorize
        
    TODO for participants:
    - Implement more sophisticated logic for determining when to stop clarifying
    - Consider issue complexity and user context in the decision
    """
    
    if state.get("needs_clarification", False):
        return "continue_clarification"
    else:
        return "categorization"