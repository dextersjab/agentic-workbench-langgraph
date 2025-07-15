"""
Clarify Issue node for HelpHub workflow.

This node analyzes user input and asks clarifying questions when needed.
"""
import logging
from typing import Dict, Any
from ..state import HelpHubState
from ..prompts.clarification_prompt import CLARIFICATION_PROMPT, ANALYSIS_PROMPT
from src.core.llm_client import client

logger = logging.getLogger(__name__)


def clarify_issue_node(state: HelpHubState) -> Dict[str, Any]:
    """
    Analyze user input and ask clarifying questions if needed.
    
    This node:
    1. Analyzes the user's input for clarity and completeness
    2. Determines if enough information exists to categorize the issue  
    3. Generates clarifying questions if needed
    4. Updates the conversation state appropriately
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with clarification decision and any questions
    """
    
    logger.info("Clarify issue node processing user input")
    
    user_input = state.get("current_user_input", "")
    messages = state.get("messages", [])
    clarification_attempts = state.get("clarification_attempts", 0)
    max_attempts = state.get("max_clarification_attempts", 3)
    
    # Build conversation history for context
    conversation_history = "\n".join([
        f"{msg.get('role', 'user')}: {msg.get('content', '')}" 
        for msg in messages[-5:]  # Last 5 messages for context
    ])
    
    try:
        # Step 1: Analyze if input needs clarification
        analysis_prompt = ANALYSIS_PROMPT.format(
            user_input=user_input,
            conversation_history=conversation_history
        )
        
        # For now, we'll implement basic LLM integration
        # In a real implementation, you would call the LLM client here
        
        # Check if input is too vague or lacks key information
        vague_indicators = [
            "broken", "not working", "problem", "issue", "help",
            "can't", "doesn't work", "error", "slow", "down"
        ]
        
        # Simple heuristic: if input is very short or only contains vague terms
        needs_clarification = (
            len(user_input.strip().split()) < 3 or
            any(indicator in user_input.lower() for indicator in vague_indicators) and
            not any(specific in user_input.lower() for specific in [
                "laptop", "computer", "printer", "email", "password", "wifi",
                "network", "server", "application", "software", "login"
            ])
        )
        
        if needs_clarification and clarification_attempts < max_attempts:
            # Generate clarifying question
            clarifying_question = generate_clarifying_question(user_input, conversation_history)
            
            state["needs_clarification"] = True
            state["clarification_attempts"] = clarification_attempts + 1
            state["current_response"] = clarifying_question
            state["custom_llm_chunk"] = clarifying_question
            
            logger.info(f"Clarification needed - attempt {clarification_attempts + 1}/{max_attempts}")
            
        else:
            # Input is clear enough or max attempts reached
            response = "Thank you for the information. Let me help you with your IT issue."
            
            state["needs_clarification"] = False
            state["current_response"] = response
            state["custom_llm_chunk"] = response
            
            logger.info("Input is clear enough - proceeding to categorization")
    
    except Exception as e:
        logger.error(f"Error in clarify_issue_node: {e}")
        # Fallback response
        state["needs_clarification"] = False
        state["current_response"] = "I'll help you with your IT issue. Let me analyze your request."
        state["custom_llm_chunk"] = "I'll help you with your IT issue. Let me analyze your request."
    
    return state


def generate_clarifying_question(user_input: str, conversation_history: str) -> str:
    """
    Generate a specific clarifying question based on the user's input.
    
    Args:
        user_input: The user's current input
        conversation_history: Previous conversation messages
        
    Returns:
        A clarifying question string
    """
    
    # Simple rule-based clarification questions
    # In a real implementation, this would use LLM to generate contextual questions
    
    user_lower = user_input.lower()
    
    if "broken" in user_lower or "not working" in user_lower:
        return "I'd like to help you with that. Can you tell me what specifically isn't working? For example, is it a device, software application, or network connection?"
    
    elif "slow" in user_lower:
        return "I understand something is running slowly. Can you tell me what specifically is slow? Is it your computer startup, a particular application, or internet browsing?"
    
    elif "error" in user_lower:
        return "I can help you with that error. Can you tell me what you were trying to do when you encountered the error, and what the error message said?"
    
    elif "can't" in user_lower or "unable" in user_lower:
        return "I'd like to help you with that access issue. Can you tell me what you're trying to access and what happens when you try?"
    
    elif "email" in user_lower:
        return "I can help with your email issue. Are you having trouble logging in, sending/receiving emails, or is there a specific error message you're seeing?"
    
    elif "password" in user_lower:
        return "I can help with your password issue. Are you trying to reset a password, or are you having trouble logging in with your current password?"
    
    elif "wifi" in user_lower or "network" in user_lower or "internet" in user_lower:
        return "I can help with your network connectivity issue. Are you unable to connect to WiFi, or is the connection slow/unstable?"
    
    else:
        return "I'd like to help you with your IT issue. Can you provide more details about what's happening and what you were trying to do?"