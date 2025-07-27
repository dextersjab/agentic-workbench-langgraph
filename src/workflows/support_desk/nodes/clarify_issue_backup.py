"""
Clarify Issue node for Support Desk workflow.

This node analyzes user input and asks clarifying questions when needed,
following the LangGraph interrupt() pattern.
"""
import logging
from copy import deepcopy

from ..state import SupportDeskState
from ..models.clarify_output import ClarifyOutput
from ..prompts.clarify_issue_prompt import CLARIFICATION_PROMPT
from ..utils import build_conversation_history
from ..utils.state_logger import log_node_start, log_node_complete
from src.core.llm_client import client
from src.core.schema_utils import pydantic_to_json_schema
from langgraph.config import get_stream_writer
from langgraph.types import interrupt

logger = logging.getLogger(__name__)


async def clarify_issue_node(state: SupportDeskState) -> SupportDeskState:
    """
    Ask a clarifying question to gather more information.
    
    This simplified node just asks for more details and returns to classification.
    No interrupt() calls - just natural flow control.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with clarifying question
    """
    
    state_before = deepcopy(state)
    state = deepcopy(state)
    
    # Log what this node will read from state
    log_node_start("clarify_issue", ["messages", "clarification_attempts", "max_clarification_attempts", "current_user_input"])
    
    messages = state.get("messages", [])
    clarification_attempts = state.get("clarification_attempts", 0)
    max_attempts = state.get("max_clarification_attempts", 3)
    
    # Build conversation history for context
    conversation_history = build_conversation_history(messages, last_n_messages=5)
    
    # Set up streaming structured output for clarification
    schema_name = "clarify_analysis"
    response_format = pydantic_to_json_schema(ClarifyOutput, schema_name)
    
    try:
        # Create prompt for clarification
        prompt = CLARIFICATION_PROMPT.format(
            user_input=state.get("current_user_input", ""),
            conversation_history=conversation_history,
            clarification_attempts=clarification_attempts,
            max_clarification_attempts=max_attempts,
            tool_name=schema_name
        )
        
        # Call LLM with structured output (no streaming of raw JSON)
        response = await client.chat_completion(
            messages=[
                {"role": "system", "content": prompt}
            ],
            model="openai/gpt-4.1",
            temperature=0.3,
            response_format=response_format,
            use_streaming=False  # Don't stream raw JSON
        )
        
        # Parse streaming structured output
        import json
        output_data = json.loads(response["content"])
        clarify_output = ClarifyOutput(**output_data)
        
        # Stream only the user-facing response text
        writer = get_stream_writer()
        writer({"custom_llm_chunk": clarify_output.response})
        
        logger.info(f"→ clarifying question (conf: {clarify_output.confidence})")
        
        # User-facing response has been streamed above
        
        # Add clarifying question to conversation
        state["messages"].append({
            "role": "assistant",
            "content": clarify_output.response
        })
        
        # Update state for next iteration
        state["clarification_attempts"] = clarification_attempts + 1
        state["current_response"] = clarify_output.response
        
    except Exception as e:
        logger.error(f"Error in clarify_issue_node: {e}")
        # Don't mask the real error with fallback messages
        # Let the error propagate for clean error handling
        raise
    
    # Log what this node wrote to state
    log_node_complete("clarify_issue", state_before, state)
    
    # Use interrupt to pause and wait for user input - outside try/catch
    # Don't pass the question to interrupt() since we already streamed it
    interrupt("Waiting for user response")
    
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