"""
Gather Info node for Support Desk workflow - Simple streaming version.

This node collects information iteratively through natural conversation.
"""
import logging
import time
from copy import deepcopy
from typing import Dict, Any

from ..state import SupportDeskState
from ..models.gather_output import GatherOutput
from ..prompts.gather_question_prompt import GATHER_QUESTION_PROMPT
from ..prompts.gather_info_prompt import INFO_GATHERING_PROMPT
from ..kb.servicehub_policy import SERVICEHUB_SUPPORT_TICKET_POLICY
from ..utils import build_conversation_history
from ..utils.state_logger import log_node_start, log_node_complete
from src.core.llm_client import client
from src.core.schema_utils import pydantic_to_openai_tool, extract_tool_call_args
from langgraph.config import get_stream_writer
from langgraph.types import interrupt

logger = logging.getLogger(__name__)


async def gather_info_node(state: SupportDeskState) -> SupportDeskState:
    """
    Collect comprehensive ticket information through iterative questioning.
    
    This node asks one question at a time using regular streaming for user experience.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with current question or completed ticket information
    """
    
    state_before = deepcopy(state)
    state = deepcopy(state)
    
    # Log what this node will read from state
    log_node_start("gather_info", ["issue_category", "issue_priority", "support_team", "messages", "gathering_round", "is_gathering_complete"])
    
    # Extract relevant information
    issue_category = state.get("issue_category", "other")
    issue_priority = state.get("issue_priority", "P2")
    support_team = state.get("support_team", "L1")
    messages = state.get("messages", [])
    
    # Track gathering progress
    gathering_round = state.get("gathering_round", 1)
    is_gathering_complete = state.get("is_gathering_complete", False)
    
    # If gathering is complete, create final ticket info
    if is_gathering_complete:
        logger.info("→ gathering complete")
        return await _create_final_ticket(state, issue_category, issue_priority, support_team, messages)
    
    # Build conversation history for context
    conversation_history = build_conversation_history(messages)
    
    try:
        # Create prompt for next question determination  
        prompt = GATHER_QUESTION_PROMPT.format(
            issue_category=issue_category,
            issue_priority=issue_priority,
            support_team=support_team,
            conversation_history=conversation_history,
            gathering_round=gathering_round,
            tool_name="gather_question"
        )
        
        # Get stream writer for streaming
        writer = get_stream_writer()
        
        # Stream callback to emit chunks as they come in
        def stream_callback(chunk: str):
            writer({"custom_llm_chunk": chunk})
        
        # Call LLM with regular streaming for natural user experience
        response = await client.chat_completion(
            messages=[
                {"role": "system", "content": prompt}
            ],
            model="openai/gpt-4.1",
            temperature=0.3,
            stream_callback=stream_callback,
            use_streaming=True
        )
        
        # Use the streamed response directly
        try:
            response_content = response.get("content", "")
            
            # Simple heuristic for completion - in production you might use a separate classification
            completion_keywords = ["complete", "sufficient", "enough information", "ready to proceed"]
            is_complete = any(keyword in response_content.lower() for keyword in completion_keywords)
            
            if is_complete:
                logger.info("→ gathering complete")
                state["is_gathering_complete"] = True
                return await _create_final_ticket(state, issue_category, issue_priority, support_team, messages)
            
            # Update state with the streamed response
            state["current_response"] = response_content
            state["gathering_round"] = gathering_round + 1
            
            # Add question to conversation history
            state["messages"].append({
                "role": "assistant",
                "content": response_content
            })
            
            logger.info(f"→ question round {gathering_round}")
            
        except Exception as e:
            logger.error(f"Error processing response: {e}")
            raise
        
    except Exception as e:
        logger.error(f"Error in gather_info_node: {e}")
        raise
    
    # Log what this node wrote to state
    log_node_complete("gather_info", state_before, state)
    
    # Use interrupt to pause and wait for user response
    interrupt("Waiting for user response to information gathering question")
    
    return state


async def _create_final_ticket(state: SupportDeskState, issue_category: str, issue_priority: str, support_team: str, messages: list) -> SupportDeskState:
    """
    Create final comprehensive ticket information from gathered conversation.
    
    Args:
        state: Current workflow state
        issue_category: Classified issue category
        issue_priority: Classified issue priority  
        support_team: Assigned support team
        messages: Conversation history
        
    Returns:
        Updated state with comprehensive ticket information
    """
    logger.info("→ creating final ticket")
    
    # Build conversation history for final analysis
    conversation_history = build_conversation_history(messages)
    
    # Set up tool for final ticket creation
    tool_name = "gather_info"
    tools = [pydantic_to_openai_tool(GatherOutput, tool_name)]
    
    # Create prompt for final ticket information extraction
    prompt = INFO_GATHERING_PROMPT.format(
        servicehub_support_ticket_policy=SERVICEHUB_SUPPORT_TICKET_POLICY,
        issue_category=issue_category,
        issue_priority=issue_priority,
        support_team=support_team,
        conversation_history=conversation_history,
        tool_name=tool_name
    )
    
    # Get stream writer
    writer = get_stream_writer()
    
    def stream_callback(chunk: str):
        writer({"custom_llm_chunk": chunk})
    
    # Call LLM for final ticket compilation using tool calls for structured data
    response = await client.chat_completion(
        messages=[
            {"role": "system", "content": prompt}
        ],
        model="openai/gpt-4.1",
        temperature=0.5,
        tools=tools,
        tool_choice="required",
        stream_callback=stream_callback,
        use_streaming=False  # Use tool calls for structured data
    )
    
    # Extract final ticket information
    output_data = extract_tool_call_args(response, tool_name)
    gather_output = GatherOutput(**output_data)
    
    # Stream the final summary manually
    writer = get_stream_writer()
    writer({"custom_llm_chunk": gather_output.response})
    
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
    
    # Update state with final ticket information
    state["ticket_info"] = ticket_info
    state["current_response"] = gather_output.response
    state["is_gathering_complete"] = True
    
    # Add final summary to conversation history
    state["messages"].append({
        "role": "assistant",
        "content": gather_output.response
    })
    
    logger.info("→ ticket created")
    
    return state


def should_continue_gathering(state: SupportDeskState) -> bool:
    """
    Determine if we should continue gathering information or proceed to ticket creation.
    
    Args:
        state: Current workflow state
        
    Returns:
        True if should continue gathering, False if ready for ticket creation
    """
    is_complete = state.get("is_gathering_complete", False)
    if is_complete:
        logger.info("→ sufficient info")
        return False
    else:
        logger.info("→ needs more info")
        return True