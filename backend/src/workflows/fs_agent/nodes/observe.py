"""
Observe node for fs_agent workflow.

This node observes the current state and plans the next file action.
"""
import logging
from copy import deepcopy
from typing import Literal

from ..state import FSAgentState
from ..models.observe_output import ObserveOutput
from ..prompts.observe_prompt import OBSERVE_PROMPT
from src.core.llm_client import client, pydantic_to_openai_tool, extract_tool_call_args

logger = logging.getLogger(__name__)


async def observe_node(state: FSAgentState) -> FSAgentState:
    """
    Observe the current state and plan the next action.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with planned action
    """
    state = deepcopy(state)
    
    logger.info("Observe node: Planning next action")
    
    # Check for repeated actions
    if state["action"]["planned_action"] and state["action"]["action_result"]:
        if state["action"]["action_result"]["success"]:
            action_type = state["action"]["planned_action"]["action_type"]
            action_path = state["action"]["planned_action"]["path"]
            action_key = f"{action_type}:{action_path}"
            
            # Increment counter
            if action_key not in state["action"]["action_counter"]:
                state["action"]["action_counter"][action_key] = 0
            state["action"]["action_counter"][action_key] += 1
            
            # Check if we're repeating too much
            if state["action"]["action_counter"][action_key] >= 2:
                logger.info(f"Detected repeated action: {action_key}")
                state["session"]["is_finished"] = True
                
                # Add completion message
                completion_message = {
                    "role": "assistant", 
                    "content": "I've completed the requested file operations. Is there anything else you'd like me to help with?"
                }
                state["messages"].append(completion_message)
                return state
    
    # Format prompt with context
    session_mode = "read-only" if state["session"]["is_read_only"] else "read-write"
    prompt = OBSERVE_PROMPT.format(
        working_directory=state["session"]["working_directory"],
        session_mode=session_mode
    )
    
    # Create tool for structured output
    observe_tool = pydantic_to_openai_tool(ObserveOutput, "observe_output")
    
    # Build conversation with action results if any
    messages = state.get("messages", [])
    if state["action"]["action_result"]:
        result = state["action"]["action_result"]
        if result["success"]:
            result_msg = f"Previous action completed successfully. Result: {result.get('result', 'Done')}"
        else:
            result_msg = f"Previous action failed: {result.get('error', 'Unknown error')}"
        messages = messages + [{"role": "system", "content": result_msg}]
    
    # Call LLM to plan next action
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            *messages
        ],
        tools=[observe_tool],
        tool_choice={"type": "function", "function": {"name": "observe_output"}}
    )
    
    # Extract the structured output
    tool_call = response.choices[0].message.tool_calls[0]
    observe_output = extract_tool_call_args(tool_call, ObserveOutput)
    
    # Update state with planned action
    if observe_output.planned_action:
        state["action"]["planned_action"] = {
            "action_type": observe_output.planned_action.action_type,
            "path": observe_output.planned_action.path,
            "content": observe_output.planned_action.content
        }
        logger.info(f"Planned action: {observe_output.planned_action.action_type} on {observe_output.planned_action.path}")
    else:
        state["action"]["planned_action"] = None
    
    state["session"]["is_finished"] = observe_output.is_finished
    
    # Add message if provided
    if observe_output.message:
        state["messages"].append({
            "role": "assistant",
            "content": observe_output.message
        })
    
    return state


def determine_action_type(state: FSAgentState) -> Literal["read", "write", "none"]:
    """
    Determine the type of the planned action for routing.
    """
    if state["session"]["is_finished"] or not state["action"]["planned_action"]:
        return "none"
    
    action_type = state["action"]["planned_action"]["action_type"]
    if action_type in ["list", "read"]:
        return "read"
    else:
        return "write"