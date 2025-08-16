"""
Router node for fs_agent workflow.

This node determines if the session will involve read-only or write operations.
"""
import logging
from copy import deepcopy
from typing import Literal

from ..state import FSAgentState
from ..models.router_output import RouterOutput
from ..prompts.router_prompt import ROUTER_PROMPT
from src.core.llm_client import client, pydantic_to_openai_tool, extract_tool_call_args

logger = logging.getLogger(__name__)


async def router_node(state: FSAgentState) -> FSAgentState:
    """
    Determine if the session will involve read-only or write operations.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with is_read_only flag set
    """
    state = deepcopy(state)
    
    logger.info("Router node: Analyzing user request")
    
    # Extract messages for context
    messages = state.get("messages", [])
    
    # Create tool for structured output
    router_tool = pydantic_to_openai_tool(RouterOutput, "router_output")
    
    # Call LLM to analyze the request
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": ROUTER_PROMPT},
            *messages
        ],
        tools=[router_tool],
        tool_choice={"type": "function", "function": {"name": "router_output"}}
    )
    
    # Extract the structured output
    tool_call = response.choices[0].message.tool_calls[0]
    router_output = extract_tool_call_args(tool_call, RouterOutput)
    
    # Update state
    state["session"]["is_read_only"] = router_output.is_read_only
    
    logger.info(f"Router decision: {'read-only' if router_output.is_read_only else 'write'} mode")
    
    # Add assistant message about the mode
    mode_message = {
        "role": "assistant",
        "content": f"I'll help you with {'exploring and reading' if router_output.is_read_only else 'file operations including writing'} files in the workspace directory."
    }
    state["messages"].append(mode_message)
    
    return state


def should_route_to_observe(state: FSAgentState) -> Literal["observe"]:
    """
    Routing function - always routes to observe after router.
    
    This is a simplified routing since we always go to observe after determining mode.
    """
    return "observe"