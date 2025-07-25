"""
Send to Desk node for Support Desk workflow.

This node formats the final response with ticket information.
"""
import logging
import time
import random
import json
from copy import deepcopy
from typing import Dict, Any

from ..state import SupportDeskState
from ..prompts.send_to_desk_prompt import FINAL_RESPONSE_PROMPT
from src.core.llm_client import client
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)


async def send_to_desk_node(state: SupportDeskState) -> SupportDeskState:
    """
    Format the final response with ticket information.
    
    This node:
    1. Creates a simulated ticket ID
    2. Formats final response with ticket ID and next steps
    3. Creates professional handoff message
    4. Provides user confirmation and tracking info
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with final response
    """
    
    logger.info("Send to desk node processing user input")
    state = deepcopy(state)
    
    # Extract ticket information
    ticket_info = state.get("ticket_info", {})
    category = ticket_info.get("category", "unknown")
    priority = ticket_info.get("priority", "medium")
    support_team = state.get("support_team", "General-Support")
    
    try:
        # Get stream writer for custom streaming
        writer = get_stream_writer()
        
        # Generate a ticket ID
        ticket_id = f"T-{int(time.time())}-{random.randint(1000, 9999)}"
        
        # Prepare final response prompt
        final_prompt = FINAL_RESPONSE_PROMPT.format(
            ticket_id=ticket_id,
            category=category,
            priority=priority,
            support_team=support_team,
            ticket_info=json.dumps(ticket_info, indent=2)
        )
        
        # Stream callback to emit chunks as they come in
        def stream_callback(chunk: str):
            writer({"custom_llm_chunk": chunk})
        
        # Call LLM to generate final response
        final_response = await client.chat_completion(
            messages=[
                {"role": "system", "content": final_prompt}
            ],
            model="openai/gpt-4.1-mini",
            temperature=0.5,
            stream_callback=stream_callback
        )
        
        # Parse the final response
        final_content = final_response.get("content", "")
        
        # Update state with final information
        state["ticket_id"] = ticket_id
        state["ticket_status"] = "created"
        state["current_response"] = final_content
        
        # Append message to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": final_content
        })
        
        logger.info(f"Ticket created successfully: {ticket_id}")
        
    except Exception as e:
        logger.error(f"Error in send_to_desk_node: {e}")
        # Error response
        error_response = f"Your support ticket has been created. A support agent from {support_team} will assist you shortly."
        
        # Generate a fallback ticket ID
        ticket_id = f"T-{int(time.time())}-ERROR"
        
        # Stream the error response
        writer = get_stream_writer()
        writer({"custom_llm_chunk": error_response})
        
        state["ticket_id"] = ticket_id
        state["ticket_status"] = "created_with_errors"
        state["current_response"] = error_response
        
        # Append message to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": error_response
        })
    
    return state