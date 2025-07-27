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

from ..state import SupportDeskState, update_state_from_output
from ..models.send_to_desk_output import SendToDeskOutput
from ..prompts.send_to_desk_prompt import FINAL_RESPONSE_PROMPT
from src.core.llm_client import client, pydantic_to_openai_tool, extract_tool_call_args
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)


async def send_to_desk_node(state: SupportDeskState) -> SupportDeskState:
    """
    Create final ticket and response using structured outputs.
    
    This node uses tool calling to generate structured SendToDeskOutput responses
    that provide complete ticket creation and user confirmation.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with final ticket information and response
    """
    
    logger.info("Send to desk node processing user input")
    state = deepcopy(state)
    
    # Extract ticket information
    ticket_info = state.get("ticket_info", {})
    issue_category = ticket_info.get("category", "other")
    issue_priority = ticket_info.get("priority", "P2")
    support_team = state.get("support_team", "L1")
    
    # Set up the tool for structured output
    tool_name = "send_to_desk"
    tools = [pydantic_to_openai_tool(SendToDeskOutput, tool_name)]
    
    try:
        # Create prompt with tool calling instruction
        prompt = FINAL_RESPONSE_PROMPT.format(
            issue_category=issue_category,
            issue_priority=issue_priority,
            support_team=support_team,
            ticket_info=json.dumps(ticket_info, indent=2),
            tool_name=tool_name
        )
        
        # Get stream writer for custom streaming
        writer = get_stream_writer()
        
        # Stream callback to emit chunks as they come in
        def stream_callback(chunk: str):
            writer({"custom_llm_chunk": chunk})
        
        # Call LLM with tools for structured output
        response = await client.chat_completion(
            messages=[
                {"role": "system", "content": prompt}
            ],
            model="openai/gpt-4.1",
            temperature=0.5,
            tools=tools,
            tool_choice="required",
            stream_callback=stream_callback
        )
        
        # Extract structured output from tool call using robust utility
        try:
            output_data = extract_tool_call_args(response, tool_name)
            desk_output = SendToDeskOutput(**output_data)
            
            logger.info(f"Final ticket creation successful: ticket_id={desk_output.ticket_id}")
            
            # Stream the final response manually since tool calls don't auto-stream
            writer = get_stream_writer()
            writer({"custom_llm_chunk": desk_output.response})
            
            # Update state with structured final information using helper
            update_state_from_output(state, desk_output, {
                'ticket_id': 'ticket_id',
                'ticket_status': 'ticket_status', 
                'assigned_team': 'assigned_team',
                'sla_commitment': 'sla_commitment',
                'next_steps': 'next_steps',
                'contact_information': 'contact_information',
                'response': 'current_response'
            })
            
            # Add response to conversation history
            state["messages"].append({
                "role": "assistant",
                "content": desk_output.response
            })
            
            logger.info(f"Ticket created successfully: {desk_output.ticket_id}")
            
        except ValueError as e:
            logger.error(f"Tool call parsing error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating SendToDeskOutput from tool call: {e}")
            raise
        
    except Exception as e:
        logger.error(f"Error in send_to_desk_node: {e}")
        # Don't mask the real error with fallback messages
        # Let the error propagate for clean error handling
        raise
    
    return state