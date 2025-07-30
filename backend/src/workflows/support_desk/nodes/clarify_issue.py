"""
Clarify Issue node for Support Desk workflow - Tool-based version.

This node analyzes user input and asks clarifying questions when needed.
"""
import logging
from copy import deepcopy

from ..state import SupportDeskState
from ..models.clarify_output import ClarifyOutput
from ..prompts.clarify_issue_prompt import CLARIFICATION_PROMPT
from ..utils import build_conversation_history
from ..utils.state_logger import log_node_start, log_node_complete
from src.core.llm_client import client, pydantic_to_openai_tool, extract_tool_call_args
from langgraph.config import get_stream_writer
from langgraph.types import interrupt

logger = logging.getLogger(__name__)


async def clarify_issue_node(state: SupportDeskState) -> SupportDeskState:
    """
    Analyze if clarification is needed and ask questions.
    
    Uses tool calls for decision making, streams questions when needed.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with clarifying question if needed
    """
    
    state_before = deepcopy(state)
    state = deepcopy(state)
    
    # Log what this node will read from state
    log_node_start("clarify_issue", ["messages", "clarification_attempts", "max_clarification_attempts", "current_user_input"])
    
    messages = state.get("messages", [])
    clarification_attempts = state.get("clarification_attempts", 0)
    max_attempts = state.get("max_clarification_attempts", 3)
    
    # Check if we're resuming (last message is our clarifying question)
    last_msg = messages[-1] if messages else None
    if last_msg and last_msg.get("role") == "assistant" and clarification_attempts > 0:
        # This is a resume - the interrupt will immediately return the user's response
        logger.info("→ resuming from interrupt")
        user_response = interrupt("Waiting for user response to clarification")
        
        # Now we can safely increment the attempts
        new_attempts = clarification_attempts + 1
        state["clarification_attempts"] = new_attempts
        logger.info(f"→ received user response, now at {new_attempts} attempts")
        
        # Log and return the updated state
        log_node_complete("clarify_issue", state_before, state)
        return state
    
    # Build conversation history for context
    conversation_history = build_conversation_history(messages)
    
    # Set up the tool for structured output
    tool_name = "clarify_analysis"
    tools = [pydantic_to_openai_tool(ClarifyOutput, tool_name)]
    
    try:
        # Create prompt for clarification analysis
        prompt = CLARIFICATION_PROMPT.format(
            user_input=state.get("current_user_input", ""),
            conversation_history=conversation_history,
            clarification_attempts=clarification_attempts,
            max_clarification_attempts=max_attempts,
            tool_name=tool_name
        )
        
        # Call LLM with tools for structured decision
        response = await client.chat_completion(
            messages=[
                {"role": "system", "content": prompt}
            ],
            model="openai/gpt-4.1",
            temperature=0.3,
            tools=tools,
            tool_choice="required"
        )
        
        # Extract structured output
        output_data = extract_tool_call_args(response, tool_name)
        clarify_output = ClarifyOutput(**output_data)
        
        logger.info(f"→ needs_clarification: {clarify_output.needs_clarification}, escalation: {clarify_output.user_requested_escalation}")
        
        # Handle based on decision
        if clarify_output.user_requested_escalation:
            # User wants to escalate - proceed without asking more questions
            logger.info("→ user requested escalation, proceeding to classification")
            # Don't ask questions, just return
            log_node_complete("clarify_issue", state_before, state)
            return state
        elif clarify_output.needs_clarification:
            # Need clarification - stream the question
            logger.info("→ streaming clarifying question")
            
            # Get stream writer for streaming
            writer = get_stream_writer()
            
            # Stream the clarifying question
            for chunk in clarify_output.response:
                writer({"custom_llm_chunk": chunk})
            
            # Add clarifying question to conversation
            state["messages"].append({
                "role": "assistant",
                "content": clarify_output.response
            })
            
            # Update state with the response
            state["current_response"] = clarify_output.response
            
            # Log what this node wrote to state before interrupt
            log_node_complete("clarify_issue", state_before, state)
            
            # Interrupt and wait for user response
            # When resumed, this will return the user's input
            user_response = interrupt("Waiting for user response to clarification")
            
            # This code only executes on resume
            # Now we can safely increment the attempts
            new_attempts = clarification_attempts + 1
            state["clarification_attempts"] = new_attempts
            logger.info(f"→ received user response, incremented to {new_attempts} attempts")
            
            return state
        else:
            # Sufficient info - proceed silently without streaming
            logger.info("→ sufficient information, proceeding to classification")
            # Don't stream anything or add to messages
            # Just return to continue workflow
            log_node_complete("clarify_issue", state_before, state)
        
    except Exception as e:
        logger.error(f"Error in clarify_issue_node: {e}")
        # Don't mask the real error with fallback messages
        # Let the error propagate for clean error handling
        raise
    
    return state


def should_continue_to_triage(state: SupportDeskState) -> bool:
    """
    Determine if we should continue to triage or ask for clarification.
    
    Args:
        state: Current workflow state
        
    Returns:
        True if ready for triage, False if need clarification
    """
    needs_clarification = state.get("needs_clarification", False)
    if needs_clarification:
        logger.info("→ needs clarification")
        return False
    else:
        logger.info("→ sufficient info")
        return True