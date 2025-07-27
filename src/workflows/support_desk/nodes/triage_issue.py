"""
Triage Issue node for Support Desk workflow.

This node routes the issue to the appropriate support team.
"""
import logging
from copy import deepcopy
from typing import Dict, Any

from ..state import SupportDeskState, update_state_from_output
from ..models.triage_output import TriageOutput
from ..prompts.triage_issue_prompt import TRIAGE_PROMPT
from ..utils import build_conversation_history
from src.core.llm_client import client, pydantic_to_openai_tool, extract_tool_call_args
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)


async def triage_issue_node(state: SupportDeskState) -> SupportDeskState:
    """
    Route the issue to the appropriate support team using structured outputs.
    
    This node uses tool calling to generate structured TriageOutput responses
    for reliable team assignment and routing decisions.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with routing and team assignment information
    """
    
    logger.info("Triage issue node processing user input")
    state = deepcopy(state)
    
    # Extract relevant information
    issue_category = state.get("issue_category", "other")
    issue_priority = state.get("issue_priority", "P2")
    messages = state.get("messages", [])
    
    # Build conversation history for context
    conversation_history = build_conversation_history(messages)
    
    # Set up the tool for structured output
    tool_name = "triage_issue"
    tools = [pydantic_to_openai_tool(TriageOutput, tool_name)]
    
    try:
        # Create prompt with tool calling instruction
        prompt = TRIAGE_PROMPT.format(
            issue_category=issue_category,
            issue_priority=issue_priority,
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
            temperature=0.3,
            tools=tools,
            tool_choice="required",
            stream_callback=stream_callback
        )
        
        # Extract structured output from tool call using robust utility
        try:
            output_data = extract_tool_call_args(response, tool_name)
            triage_output = TriageOutput(**output_data)
            
            logger.info(f"Triage successful: team={triage_output.support_team}, "
                       f"resolution_time={triage_output.estimated_resolution_time}")
            
            # Update state with structured triage information using helper
            update_state_from_output(state, triage_output, {
                'support_team': 'support_team',
                'estimated_resolution_time': 'estimated_resolution_time',
                'escalation_path': 'escalation_path',
                'response': 'current_response'
            })
            
            # Add response to conversation history
            state["messages"].append({
                "role": "assistant",
                "content": triage_output.response
            })
            
            logger.info(f"Issue triaged to {triage_output.support_team} team")
            
        except ValueError as e:
            logger.error(f"Tool call parsing error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating TriageOutput from tool call: {e}")
            raise
        
    except Exception as e:
        logger.error(f"Error in triage_issue_node: {e}")
        # Don't mask the real error with fallback messages
        # Let the error propagate for clean error handling
        raise
    
    return state