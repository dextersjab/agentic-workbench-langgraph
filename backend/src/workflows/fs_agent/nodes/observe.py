"""
Observe node for fs_agent workflow.

This node observes the current state and plans the next file action.
On first interaction, it also determines if the session should be read-only or allow writes.
"""
import logging
from copy import deepcopy
from typing import Literal

from ..state import FSAgentState
from ..models.observe_output import ObserveOutput
from ..prompts.observe_prompt import OBSERVE_PROMPT
from src.core.state_logger import log_node_start, log_node_complete
from src.core.llm_client import client, pydantic_to_openai_tool, extract_tool_call_args
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)


async def observe_node(state: FSAgentState) -> FSAgentState:
    """
    Observe the current state and plan the next action.
    On first interaction, also determine read-only vs write mode.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with planned action and mode (if first interaction)
    """
    state_before = deepcopy(state)
    state = deepcopy(state)
    
    # Log what this node will read from state
    log_node_start("observe", ["messages", "session", "action"], state)
    
    # Check if this is the first interaction
    is_first = state["session"]["is_first_interaction"]
    
    # Check for repeated actions (skip on first interaction)
    if not is_first and state["action"]["planned_action"] and state["action"]["action_result"]:
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
                
                # Log what this node wrote to state
                log_node_complete("observe", state_before, state)
                return state
    
    # Format prompt based on whether this is first interaction
    if is_first:
        mode_context = "This is the first interaction. Determine if the user needs write operations."
        task_instruction = """First, analyze the user's request to determine the operation mode:
- If they want to create, write, modify, or delete files, set is_read_only to False
- If they only want to explore, list, or read files, set is_read_only to True

Then, plan the first file action based on their request."""
        read_only_instruction = "Set based on whether write operations are needed"
        write_restriction = "(requires write mode)"
    else:
        session_mode = "read-only" if state["session"]["is_read_only"] else "read-write"
        mode_context = f"Session mode: {session_mode}"
        task_instruction = "Based on the conversation history and any previous action results, determine the next action to take."
        read_only_instruction = "Leave as None (already determined)"
        write_restriction = "(only if not in read-only mode)" if state["session"]["is_read_only"] else ""
    
    prompt = OBSERVE_PROMPT.format(
        working_directory=state["session"]["working_directory"],
        mode_context=mode_context,
        task_instruction=task_instruction,
        read_only_instruction=read_only_instruction,
        write_restriction=write_restriction
    )
    
    # Get stream writer for real-time feedback
    writer = get_stream_writer()
    
    # Create tool for structured output
    observe_tool = pydantic_to_openai_tool(ObserveOutput, "observe_output")
    
    # Build conversation with action results if any
    messages = state.get("messages", [])
    if state["action"]["action_result"] and not is_first:
        result = state["action"]["action_result"]
        if result["success"]:
            result_msg = f"Previous action completed successfully. Result: {result.get('result', 'Done')}"
        else:
            result_msg = f"Previous action failed: {result.get('error', 'Unknown error')}"
        messages = messages + [{"role": "system", "content": result_msg}]
    
    # Buffer to collect the response
    response_buffer = []
    
    # Stream callback to emit chunks and collect them
    def stream_callback(chunk: str):
        writer({"custom_llm_chunk": chunk})
        response_buffer.append(chunk)
    
    # Call LLM to plan next action (and determine mode if first interaction)
    response = await client.chat_completion(
        messages=[
            {"role": "system", "content": prompt},
            *messages
        ],
        model="openai/gpt-4.1-mini",
        temperature=0.7,
        tools=[observe_tool],
        tool_choice="required",
        stream_callback=stream_callback,
        use_streaming=True
    )
    
    # Extract the structured output
    output_data = extract_tool_call_args(response, "observe_output")
    observe_output = ObserveOutput(**output_data)
    
    # Handle first interaction mode setting
    if is_first:
        state["session"]["is_first_interaction"] = False
        if observe_output.is_read_only is not None:
            state["session"]["is_read_only"] = observe_output.is_read_only
            
            # Stream mode announcement
            mode_text = f"\n\nI'll help you with {'exploring and reading' if observe_output.is_read_only else 'file operations including writing'} files in the workspace directory.\n\n"
            writer({"custom_llm_chunk": mode_text})
            
            # Add to state for history
            mode_message = {
                "role": "assistant",
                "content": mode_text
            }
            state["messages"].append(mode_message)
    
    # Update state with planned action
    if observe_output.planned_action:
        # Check if action is allowed in current mode
        if state["session"]["is_read_only"] and observe_output.planned_action.action_type in ["write", "delete"]:
            logger.warning(f"Write operation requested in read-only mode: {observe_output.planned_action.action_type}")
            state["session"]["is_finished"] = True
            error_message = {
                "role": "assistant",
                "content": "I'm currently in read-only mode and cannot perform write or delete operations. If you need to modify files, please start a new session with a request that clearly indicates you want to create, modify, or delete files."
            }
            state["messages"].append(error_message)
            
            # Log what this node wrote to state
            log_node_complete("observe", state_before, state)
            return state
        
        state["action"]["planned_action"] = {
            "action_type": observe_output.planned_action.action_type,
            "path": observe_output.planned_action.path,
            "content": observe_output.planned_action.content
        }
    else:
        state["action"]["planned_action"] = None
    
    state["session"]["is_finished"] = observe_output.is_finished
    
    # Stream and add message if provided (and not already added mode message)
    if observe_output.message and not (is_first and observe_output.is_read_only is not None):
        writer({"custom_llm_chunk": f"\n{observe_output.message}\n"})
        state["messages"].append({
            "role": "assistant",
            "content": observe_output.message
        })
    
    # Log what this node wrote to state
    log_node_complete("observe", state_before, state)
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