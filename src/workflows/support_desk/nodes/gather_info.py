"""
Gather Info node for Support Desk workflow.

This node collects additional information needed for the support team.
"""
import logging
import time
from copy import deepcopy
from typing import Dict, Any

from ..state import SupportDeskState
from ..prompts.gather_info_prompt import INFO_GATHERING_PROMPT
from ..utils import build_conversation_history
from src.core.llm_client import client
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)


async def gather_info_node(state: SupportDeskState) -> SupportDeskState:
    """
    Collect additional information needed for the support team.
    
    This node:
    1. Determines what information the support team needs
    2. Collects user details, context, urgency
    3. Updates the workflow state with complete ticket information
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with complete ticket information
    """
    
    logger.info("Gather info node processing user input")
    state = deepcopy(state)
    
    # Extract relevant information
    category = state.get("issue_category", "unknown")
    priority = state.get("issue_priority", "medium")
    support_team = state.get("support_team", "General-Support")
    messages = state.get("messages", [])
    
    # Build conversation history for context
    conversation_history = build_conversation_history(messages)
    
    try:
        # Get stream writer for custom streaming
        writer = get_stream_writer()
        
        # Prepare info gathering prompt
        info_prompt = INFO_GATHERING_PROMPT.format(
            category=category,
            priority=priority,
            support_team=support_team,
            conversation_history=conversation_history
        )
        
        # Stream callback to emit chunks as they come in
        def stream_callback(chunk: str):
            writer({"custom_llm_chunk": chunk})
        
        # Call LLM to gather information
        info_response = await client.chat_completion(
            messages=[
                {"role": "system", "content": info_prompt}
            ],
            model="openai/gpt-4.1-mini",
            temperature=0.5,
            stream_callback=stream_callback
        )
        
        # Parse the information gathering response
        info_content = info_response.get("content", "")
        
        # Create ticket information dictionary
        ticket_info = {
            "category": category,
            "priority": priority,
            "support_team": support_team,
            "description": info_content,
            "timestamp": time.time(),
            "status": "new"
        }
        
        # Update state with ticket information
        state["ticket_info"] = ticket_info
        state["current_response"] = info_content
        
        # Append message to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": info_content
        })
        
        logger.info("Ticket information gathered successfully")
        
    except Exception as e:
        logger.error(f"Error in gather_info_node: {e}")
        # Error response
        error_response = "I'm gathering the necessary information for your support ticket."
        
        # Stream the error response
        writer = get_stream_writer()
        writer({"custom_llm_chunk": error_response})
        
        # Create minimal ticket information
        ticket_info = {
            "category": category,
            "priority": priority,
            "support_team": support_team,
            "description": "Issue requires attention",
            "timestamp": time.time(),
            "status": "new"
        }
        
        state["ticket_info"] = ticket_info
        state["current_response"] = error_response
        
        # Append message to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": error_response
        })
    
    return state