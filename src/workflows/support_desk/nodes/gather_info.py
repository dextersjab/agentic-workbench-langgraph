"""
Gather Info node for Support Desk workflow.

This node collects additional information needed for the support team.
"""
import logging
import time
from copy import deepcopy
from typing import Dict, Any

from ..state import SupportDeskState
from ..models.gather_output import GatherOutput
from ..prompts.gather_info_prompt import INFO_GATHERING_PROMPT
from ..utils import build_conversation_history
from src.core.llm_client import client, pydantic_to_openai_tool, extract_tool_call_args
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)


async def gather_info_node(state: SupportDeskState) -> SupportDeskState:
    """
    Collect comprehensive ticket information using structured outputs.
    
    This node uses tool calling to generate structured GatherOutput responses
    that compile all necessary information for the support ticket.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with comprehensive ticket information
    """
    
    logger.info("Gather info node processing user input")
    state = deepcopy(state)
    
    # Extract relevant information
    issue_category = state.get("issue_category", "other")
    issue_priority = state.get("issue_priority", "P2")
    support_team = state.get("support_team", "L1")
    messages = state.get("messages", [])
    
    # Build conversation history for context
    conversation_history = build_conversation_history(messages)
    
    # Set up the tool for structured output
    tool_name = "gather_info"
    tools = [pydantic_to_openai_tool(GatherOutput, tool_name)]
    
    try:
        # Create prompt with tool calling instruction
        prompt = INFO_GATHERING_PROMPT.format(
            issue_category=issue_category,
            issue_priority=issue_priority,
            support_team=support_team,
            conversation_history=conversation_history,
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
            gather_output = GatherOutput(**output_data)
            
            logger.info(f"Info gathering successful: summary='{gather_output.ticket_summary[:50]}...'")
            
            # Create comprehensive ticket information dictionary
            ticket_info = {
                "category": issue_category,
                "priority": issue_priority,
                "support_team": support_team,
                "summary": gather_output.ticket_summary,
                "description": gather_output.detailed_description,
                "affected_systems": gather_output.affected_systems,
                "user_impact": gather_output.user_impact,
                "reproduction_steps": gather_output.reproduction_steps,
                "metadata": gather_output.additional_metadata,
                "timestamp": time.time(),
                "status": "new"
            }
            
            # Update state with structured ticket information
            state["ticket_info"] = ticket_info
            state["current_response"] = gather_output.response
            
            # Add response to conversation history
            state["messages"].append({
                "role": "assistant",
                "content": gather_output.response
            })
            
            logger.info("Comprehensive ticket information gathered successfully")
            
        except ValueError as e:
            logger.error(f"Tool call parsing error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating GatherOutput from tool call: {e}")
            raise
        
    except Exception as e:
        logger.error(f"Error in gather_info_node: {e}")
        # Fallback information gathering
        error_response = "I'm gathering the necessary information for your support ticket."
        
        # Stream the error response
        writer = get_stream_writer()
        writer({"custom_llm_chunk": error_response})
        
        # Create minimal ticket information
        ticket_info = {
            "category": issue_category,
            "priority": issue_priority,
            "support_team": support_team,
            "summary": "IT Support Request",
            "description": "Issue requires attention",
            "affected_systems": [],
            "user_impact": "To be determined",
            "reproduction_steps": [],
            "metadata": {},
            "timestamp": time.time(),
            "status": "new"
        }
        
        state["ticket_info"] = ticket_info
        state["current_response"] = error_response
        
        # Add fallback response to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": error_response
        })
    
    return state