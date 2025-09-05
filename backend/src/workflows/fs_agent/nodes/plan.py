"""
Plan node for fs_agent workflow.

This node implements the reasoning/thinking step of the ReAct pattern,
with self-referential "think" loops for deeper reflection.
"""
import logging
from copy import deepcopy
from typing import Literal

from ..state import FSAgentState
from ..models.plan_output import PlanOutput
from ..prompts.plan_prompt import REASONING_PROMPT, DECISION_PROMPT, FORCE_ACTION_PROMPT_ADDITION
from ..business_context import MAX_THINKING_ITERATIONS
from src.core.state_logger import log_node_start, log_node_complete
from src.core.llm_client import client, pydantic_to_openai_tool, extract_tool_call_args
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)


async def plan_node(state: FSAgentState) -> FSAgentState:
    """
    Plan the next action with explicit reasoning and optional deeper thinking.
    
    This node implements the ReAct pattern's reasoning step, with the ability
    to loop back on itself for deeper reflection (up to MAX_THINKING_ITERATIONS).
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with planning results and potential action
    """
    state_before = deepcopy(state)
    
    # Log what this node will read from state
    log_node_start("plan", ["messages", "session", "action", "planning"], state)
    
    # Get stream writer for real-time feedback
    writer = get_stream_writer()
    
    # Get current thinking state
    thinking_iterations = state["planning"]["thinking_iterations"]
    force_action = thinking_iterations >= MAX_THINKING_ITERATIONS
    
    # Stream thinking header with tags
    if thinking_iterations == 0:
        writer({"custom_llm_chunk": "\n<thought>\n"})
    else:
        writer({"custom_llm_chunk": f"\n<thought iteration=\"{thinking_iterations + 1}/{MAX_THINKING_ITERATIONS}\">\n"})
    
    # Build context for prompt
    session_mode = "read-only" if state["session"]["is_read_only"] else "read-write"
    
    # Build action history summary
    action_history = []
    if state["action"]["action_result"]:
        result = state["action"]["action_result"]
        if result["success"]:
            action_history.append(f"Previous action succeeded: {result.get('result', 'Done')}")
        else:
            action_history.append(f"Previous action failed: {result.get('error', 'Unknown error')}")
    
    action_history_str = "\n".join(action_history) if action_history else "No previous actions in this session."
    
    # Build task status
    if state["session"]["is_finished"]:
        task_status = "Task appears to be complete."
    elif state["action"]["planned_action"]:
        task_status = f"Previously planned: {state['action']['planned_action']['action_type']} on {state['action']['planned_action']['path']}"
    else:
        task_status = "No action currently planned."
    
    # Set task instruction based on force_action
    if force_action:
        task_instruction = "You MUST decide on a concrete action now. You have reached the maximum thinking iterations."
        force_action_instruction = FORCE_ACTION_PROMPT_ADDITION.format(max_thinking_iterations=MAX_THINKING_ITERATIONS)
    else:
        task_instruction = "Think carefully about the best next action. You can choose to think deeper if needed."
        force_action_instruction = ""
    
    # Set write restriction based on mode
    write_restriction = "(not available in read-only mode)" if state["session"]["is_read_only"] else ""
    
    # Stage 1: Create reasoning prompt (no tools)
    reasoning_prompt = REASONING_PROMPT.format(
        working_directory=state["session"]["working_directory"],
        session_mode=session_mode,
        thinking_iteration=thinking_iterations + 1,
        max_thinking_iterations=MAX_THINKING_ITERATIONS,
        action_history=action_history_str,
        task_status=task_status,
        task_instruction=task_instruction,
        force_action_instruction=force_action_instruction,
        write_restriction=write_restriction
    )
    
    # Buffer to collect the reasoning response
    reasoning_buffer = []
    
    # Stream callback to emit chunks and collect them
    def stream_callback(chunk: str):
        writer({"custom_llm_chunk": chunk})
        reasoning_buffer.append(chunk)
    
    try:
        # Stage 1: Stream pure reasoning without tools
        reasoning_response = await client.chat_completion(
            messages=[
                {"role": "system", "content": reasoning_prompt},
                *state["messages"]
            ],
            model="openai/gpt-4.1-mini",
            temperature=0.7,
            stream_callback=stream_callback,
            use_streaming=True
            # NO TOOLS - pure reasoning
        )
        
        # Get the complete reasoning
        reasoning_content = "".join(reasoning_buffer)
        
        # Stage 2: Create decision prompt with structured output
        decision_prompt = DECISION_PROMPT.format(
            max_thinking_iterations=MAX_THINKING_ITERATIONS,
            force_action_instruction=force_action_instruction if force_action else ""
        )
        
        # Create tool for structured output
        plan_tool = pydantic_to_openai_tool(PlanOutput, "plan_tool")
        
        # Stage 2: Make structured decision based on reasoning
        decision_response = await client.chat_completion(
            messages=[
                {"role": "system", "content": decision_prompt},
                {"role": "assistant", "content": reasoning_content},  # Include the reasoning
                {"role": "user", "content": "Make your decision based on the reasoning above."}
            ],
            model="openai/gpt-4.1-mini",
            temperature=0.3,  # Lower temperature for decision
            tools=[plan_tool],
            tool_choice="required",
            use_streaming=False  # No streaming for structured output
        )
        
        # Extract structured output from tool call
        output_data = extract_tool_call_args(decision_response, "plan_tool")
        plan_output = PlanOutput(**output_data)
        
        logger.info(f"→ planning complete: confidence={plan_output.confidence_level}, needs_thinking={plan_output.needs_deeper_thinking}")
        
        # Update planning state
        state["planning"]["thinking_iterations"] = thinking_iterations + 1
        state["planning"]["needs_deeper_thinking"] = plan_output.needs_deeper_thinking and not force_action
        state["planning"]["current_reasoning"] = plan_output.reasoning
        state["planning"]["alternative_approaches"] = plan_output.alternative_approaches
        
        # Update action state if we have a plan
        if plan_output.planned_action:
            state["action"]["planned_action"] = {
                "action_type": plan_output.planned_action.action_type,
                "path": plan_output.planned_action.path,
                "content": plan_output.planned_action.content
            }
            logger.info(f"→ planned action: {plan_output.planned_action.action_type} on {plan_output.planned_action.path}")
        else:
            state["action"]["planned_action"] = None
        
        # Update session state
        state["session"]["is_finished"] = plan_output.is_finished
        
        # Close the thought tag
        writer({"custom_llm_chunk": "\n</thought>\n"})
        
        # Only show action summary if we have a concrete plan (not just thinking)
        if plan_output.planned_action and (not plan_output.needs_deeper_thinking or force_action):
            action_summary = f"**Next:** {plan_output.planned_action.action_type} {plan_output.planned_action.path}"
            writer({"custom_llm_chunk": f"\n{action_summary}\n"})
        
    except Exception as e:
        logger.error(f"Error in plan_node: {e}")
        # Close the thought tag even on error
        writer({"custom_llm_chunk": "\n</thought>\n"})
        # Set fallback state
        state["planning"]["needs_deeper_thinking"] = False
        state["action"]["planned_action"] = None
        raise
    
    # Log what this node wrote to state
    log_node_complete("plan", state_before, state)
    
    return state


def route_by_safety(state: FSAgentState) -> Literal["safe", "risky", "none"]:
    """
    Route actions based on safety: safe actions execute directly, risky ones need approval.
    
    Args:
        state: Current workflow state
        
    Returns:
        "safe" for list/read operations that can execute directly
        "risky" for write/edit/delete operations that need approval
        "none" if finished or no action planned
    """
    # Check if we're finished
    if state["session"]["is_finished"]:
        logger.info("→ task finished")
        return "none"
    
    # Route based on planned action
    planned_action = state["action"]["planned_action"]
    if not planned_action:
        logger.info("→ no action planned, ending")
        return "none"
    
    action_type = planned_action["action_type"]
    
    # Safe operations can execute directly
    if action_type in ["list", "read"]:
        logger.info(f"→ routing to safe execution for {action_type}")
        return "safe"
    
    # Risky operations need approval
    elif action_type in ["write", "edit", "delete"]:
        # Check if file exists for write operations (new vs overwrite)
        if action_type == "write":
            import os
            file_path = planned_action["path"]
            working_dir = state["session"]["working_directory"]
            
            if not os.path.isabs(file_path):
                if file_path == working_dir or file_path.startswith(f"{working_dir}/"):
                    full_path = file_path
                else:
                    full_path = os.path.join(working_dir, file_path)
            else:
                full_path = file_path
            
            if os.path.exists(full_path):
                logger.info(f"→ routing to risky (overwrite) for {action_type}")
                return "risky"
            else:
                # New file creation is safe(r)
                logger.info(f"→ routing to safe (new file) for {action_type}")
                return "safe"
        else:
            # edit and delete are always risky
            logger.info(f"→ routing to risky for {action_type}")
            return "risky"
    
    else:
        logger.warning(f"→ unknown action type: {action_type}")
        return "none"


def should_continue_planning(state: FSAgentState) -> Literal["think", "safe", "risky", "none"]:
    """
    Determine routing from plan node.
    
    Args:
        state: Current workflow state
        
    Returns:
        "think" if needs deeper thinking and hasn't hit limit
        "safe"/"risky" based on action safety level
        "none" if finished or no action planned
    """
    planning = state["planning"]
    
    # Check if we need more thinking (and haven't hit limit)
    if planning["needs_deeper_thinking"] and planning["thinking_iterations"] < MAX_THINKING_ITERATIONS:
        logger.info(f"→ continuing to think (iteration {planning['thinking_iterations']}/{MAX_THINKING_ITERATIONS})")
        return "think"
    
    # Route based on action safety
    return route_by_safety(state)