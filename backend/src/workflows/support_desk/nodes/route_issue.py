"""
Route Issue node for Support Desk workflow.

This node routes the issue to the appropriate support team.
"""
import logging
from copy import deepcopy

from ..state import SupportDeskState, update_state_from_output
from ..models.route_output import RouteOutput
from ..prompts.route_issue_prompt import ROUTE_PROMPT
from ..utils import build_conversation_history
from src.core.state_logger import log_node_start, log_node_complete
from src.core.llm_client import client, pydantic_to_openai_tool, extract_tool_call_args
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)


async def route_issue_node(state: SupportDeskState) -> SupportDeskState:
    """
    Route the issue to the appropriate support team using structured outputs.
    
    This node uses tool calling to generate structured RouteOutput responses
    for reliable team assignment and routing decisions.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with routing and team assignment information
    """
    
    state_before = deepcopy(state)
    
    # Log what this node will read from state
    log_node_start("route_issue", ["issue_category", "issue_priority", "messages"])
    
    # Extract relevant information from nested state
    issue_category = state.get("classification", {}).get("issue_category", "other")
    issue_priority = state.get("classification", {}).get("issue_priority", "P2")
    messages = state.get("conversation", {}).get("messages", [])
    
    # Build conversation history for context
    conversation_history = build_conversation_history(messages)
    
    # Set up the tool for structured output
    tool_name = "route_issue"
    tools = [pydantic_to_openai_tool(RouteOutput, tool_name)]
    
    try:
        # Create prompt with tool calling instruction
        prompt = ROUTE_PROMPT.format(
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
            route_output = RouteOutput(**output_data)
            
            logger.info(f"→ {route_output.support_team} team ({route_output.estimated_resolution_time})")
            
            # DON'T stream - this is internal processing, not user-facing
            # Routing happens silently and routes to gather_info
            
            # Update state with structured routing information using helper
            update_state_from_output(state, route_output, {
                'support_team': 'assigned_team',
                'estimated_resolution_time': 'estimated_resolution_time',
                'escalation_path': 'escalation_path'
            })
            
            # DON'T add to conversation history - this is internal routing
            # The user doesn't need to see "Your issue has been assigned to L1..."
            
            logger.info("→ routing complete")
            
        except ValueError as e:
            logger.error(f"Tool call parsing error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating RouteOutput from tool call: {e}")
            raise
        
    except Exception as e:
        logger.error(f"Error in route_issue_node: {e}")
        # Don't mask the real error with fallback messages
        # Let the error propagate for clean error handling
        raise
    
    # Log what this node wrote to state
    log_node_complete("route_issue", state_before, state)
    
    return state