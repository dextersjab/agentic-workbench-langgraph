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
from ..utils.state_logger import log_node_start, log_node_complete
from src.core.llm_client import client
from src.core.schema_utils import pydantic_to_json_schema
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
    
    state_before = deepcopy(state)
    state = deepcopy(state)
    
    # Log what this node will read from state
    log_node_start("send_to_desk", ["ticket_info", "support_team"])
    
    # Extract ticket information
    ticket_info = state.get("ticket_info", {})
    issue_category = ticket_info.get("category", "other")
    issue_priority = ticket_info.get("priority", "P2")
    support_team = state.get("support_team", "L1")
    
    # Set up streaming structured output for final response
    schema_name = "send_to_desk"
    response_format = pydantic_to_json_schema(SendToDeskOutput, schema_name)
    
    try:
        # Create prompt for final response
        prompt = FINAL_RESPONSE_PROMPT.format(
            issue_category=issue_category,
            issue_priority=issue_priority,
            support_team=support_team,
            ticket_info=json.dumps(ticket_info, indent=2),
            tool_name=schema_name
        )
        
        # Call LLM with structured output (no streaming of raw JSON)
        response = await client.chat_completion(
            messages=[
                {"role": "system", "content": prompt}
            ],
            model="openai/gpt-4.1",
            temperature=0.5,
            response_format=response_format,
            use_streaming=False  # Don't stream raw JSON
        )
        
        # Parse streaming structured output
        try:
            import json
            output_data = json.loads(response["content"])
            desk_output = SendToDeskOutput(**output_data)
            
            # Stream only the user-facing response text
            writer = get_stream_writer()
            writer({"custom_llm_chunk": desk_output.response})
            
            logger.info(f"→ ticket {desk_output.ticket_id} created")
            
            # User-facing response has been streamed above
            
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
            
            logger.info("→ desk submission complete")
            
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
    
    # Log what this node wrote to state
    log_node_complete("send_to_desk", state_before, state)
    
    return state