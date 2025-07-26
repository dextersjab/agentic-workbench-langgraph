"""
Clarify Issue node for Support Desk workflow.

This node analyzes user input and asks clarifying questions when needed.
"""
import logging
from copy import deepcopy
from typing import Dict, Any

from ..state import SupportDeskState
from ..prompts.clarify_issue_prompt import ANALYSIS_PROMPT, CLARIFICATION_PROMPT
from ..utils import build_conversation_history
from src.core.llm_client import client
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)


async def clarify_issue_node(state: SupportDeskState) -> SupportDeskState:
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
    state = deepcopy(state)
    
    user_input = state.get("current_user_input", "")
    messages = state.get("messages", [])
    clarification_attempts = state.get("clarification_attempts", 0)
    max_attempts = state.get("max_clarification_attempts", 3)
    
    # Build conversation history for context
    conversation_history = build_conversation_history(messages, last_n_messages=5)
    
    try:
        # Step 1: Analyze if input needs clarification using LLM
        analysis_prompt = ANALYSIS_PROMPT.format(
            user_input=user_input,
            conversation_history=conversation_history
        )
        
        # Call LLM to analyze if clarification is needed
        analysis_response = await client.chat_completion(
            messages=[
                {"role": "system", "content": analysis_prompt}
            ],
            model="openai/gpt-4.1-mini",
            temperature=0.3
        )
        
        # Parse the analysis response to determine if clarification is needed
        analysis_content = analysis_response.get("content", "").lower()
        needs_clarification = (
            "needs_clarification" in analysis_content or
            "needs clarification" in analysis_content or
            "clarification needed" in analysis_content or
            "more information" in analysis_content
        ) and clarification_attempts < max_attempts
        
        # Get stream writer for custom streaming
        writer = get_stream_writer()
        
        if needs_clarification:
            # Generate clarifying question using LLM
            clarification_prompt = CLARIFICATION_PROMPT.format(
                user_input=user_input,
                conversation_history=conversation_history,
                attempt_number=clarification_attempts + 1,
                max_attempts=max_attempts
            )
            
            # Stream callback to emit chunks as they come in
            def stream_callback(chunk: str):
                writer({"custom_llm_chunk": chunk})
            
            clarification_response = await client.chat_completion(
                messages=[
                    {"role": "system", "content": clarification_prompt}
                ],
                model="openai/gpt-4.1-mini",
                temperature=0.7,
                stream_callback=stream_callback
            )
            
            clarifying_question = clarification_response.get("content", "")
            
            state["needs_clarification"] = True
            state["clarification_attempts"] = clarification_attempts + 1
            state["current_response"] = clarifying_question
            
            # Append message to conversation history
            state["messages"].append({
                "role": "assistant",
                "content": clarifying_question
            })
            
            logger.info(f"Clarification needed - attempt {clarification_attempts + 1}/{max_attempts}")
            
        else:
            # Input is clear enough or max attempts reached
            response = "Thank you for the information. Let me help you with your IT issue."
            
            # Stream the static response
            writer({"custom_llm_chunk": response})
            
            state["needs_clarification"] = False
            state["current_response"] = response
            
            # Append message to conversation history
            state["messages"].append({
                "role": "assistant",
                "content": response
            })
            
            logger.info("Input is clear enough - proceeding to categorization")
    
    except Exception as e:
        logger.error(f"Error in clarify_issue_node: {e}")
        # Error response - still needs to be properly formatted
        error_response = "I'll help you with your IT issue. Let me analyze your request."
        
        # Stream the error response
        writer = get_stream_writer()
        writer({"custom_llm_chunk": error_response})
        
        state["needs_clarification"] = False
        state["current_response"] = error_response
        
        # Append message to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": error_response
        })
    
    return state