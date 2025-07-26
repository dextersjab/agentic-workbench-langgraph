"""
Triage Issue node for Support Desk workflow.

This node routes the issue to the appropriate support team.
"""
import logging
from copy import deepcopy
from typing import Dict, Any

from ..state import SupportDeskState
from ..prompts.triage_issue_prompt import TRIAGE_PROMPT
from ..utils import build_conversation_history
from src.core.llm_client import client
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)


async def triage_issue_node(state: SupportDeskState) -> SupportDeskState:
    """
    Route the issue to the appropriate support team.
    
    This node:
    1. Determines the appropriate support team based on category
    2. Assesses priority based on business impact
    3. Routes to: L1 support, specialist, escalation
    4. Updates the workflow state with routing information
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with routing information
    """
    
    logger.info("Triage issue node processing user input")
    state = deepcopy(state)
    
    # Extract relevant information
    category = state.get("issue_category", "unknown")
    priority = state.get("issue_priority", "medium")
    messages = state.get("messages", [])
    
    # Build conversation history for context
    conversation_history = build_conversation_history(messages)
    
    try:
        # Get stream writer for custom streaming
        writer = get_stream_writer()
        
        # Prepare triage prompt
        triage_prompt = TRIAGE_PROMPT.format(
            category=category,
            conversation_history=conversation_history
        )
        
        # Stream callback to emit chunks as they come in
        def stream_callback(chunk: str):
            writer({"custom_llm_chunk": chunk})
        
        # Call LLM to triage the issue
        triage_response = await client.chat_completion(
            messages=[
                {"role": "system", "content": triage_prompt}
            ],
            model="openai/gpt-4.1-mini",
            temperature=0.3,
            stream_callback=stream_callback
        )
        
        # Parse the triage response
        triage_content = triage_response.get("content", "")
        
        # Determine support team based on category and priority
        # This is a simplified implementation - in a real system, we would use
        # structured output parsing or function calling
        if category == "hardware":
            support_team = "L1-Hardware"
        elif category == "software":
            support_team = "L2-Software"
        elif category == "access":
            support_team = "Security-Team"
        else:
            support_team = "General-Support"
        
        # For high priority issues, escalate
        if priority == "high":
            support_team = f"Escalated-{support_team}"
        
        # Update state with triage information
        state["support_team"] = support_team
        state["current_response"] = triage_content
        
        # Append message to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": triage_content
        })
        
        logger.info(f"Issue triaged to {support_team}")
        
    except Exception as e:
        logger.error(f"Error in triage_issue_node: {e}")
        # Error response
        error_response = "I'm determining the priority of your issue and routing it to the appropriate team."
        
        # Stream the error response
        writer = get_stream_writer()
        writer({"custom_llm_chunk": error_response})
        
        # Default team based on category
        if category == "hardware":
            support_team = "L1-Hardware"
        elif category == "software":
            support_team = "L2-Software"
        elif category == "access":
            support_team = "Security-Team"
        else:
            support_team = "General-Support"
            
        state["support_team"] = support_team
        state["current_response"] = error_response
        
        # Append message to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": error_response
        })
    
    return state