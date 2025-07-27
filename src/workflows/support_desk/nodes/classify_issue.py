"""
Classify Issue node for Support Desk workflow.

This node categorizes the IT issue into predefined categories.
"""
import logging
from copy import deepcopy
from typing import Dict, Any

from ..state import SupportDeskState
from ..models.classify_output import ClassifyOutput
from ..prompts.classify_issue_prompt import CLASSIFICATION_PROMPT
from ..utils import build_conversation_history
from ..utils.state_logger import log_node_start, log_node_complete
from src.core.llm_client import client, pydantic_to_openai_tool, extract_tool_call_args
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)


async def classify_issue_node(state: SupportDeskState) -> SupportDeskState:
    """
    Categorize the IT issue using structured outputs.
    
    This node uses tool calling to generate structured ClassifyOutput responses
    for reliable issue categorization and priority assignment.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with category and priority information
    """
    
    state_before = deepcopy(state)
    state = deepcopy(state)
    
    # Log what this node will read from state
    log_node_start("classify_issue", ["messages"])
    
    # Extract conversation history for context
    messages = state.get("messages", [])
    conversation_history = build_conversation_history(messages)
    
    # Check if we've exhausted clarification attempts
    clarification_attempts = state.get("clarification_attempts", 0)
    max_attempts = state.get("max_clarification_attempts", 3)
    force_proceed = clarification_attempts >= max_attempts
    
    # Set up the tool for structured output
    tool_name = "classify_issue"
    tools = [pydantic_to_openai_tool(ClassifyOutput, tool_name)]
    
    try:
        # Create prompt with tool calling instruction
        prompt = CLASSIFICATION_PROMPT.format(
            conversation_history=conversation_history,
            tool_name=tool_name,
            clarification_attempts=clarification_attempts,
            max_clarification_attempts=max_attempts,
            force_proceed=force_proceed
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
            classify_output = ClassifyOutput(**output_data)
            
            logger.info(f"→ {classify_output.category}/{classify_output.priority} (conf: {classify_output.confidence})")
            
            # Check if clarification is needed (unless we've hit the limit)
            if classify_output.needs_clarification and not force_proceed:
                logger.info("→ needs clarification")
                state["needs_clarification"] = True
                state["current_response"] = classify_output.response
                
                # Add clarifying question to conversation
                state["messages"].append({
                    "role": "assistant",
                    "content": classify_output.response
                })
            else:
                logger.info("→ classification complete")
                
                # DON'T stream - this is internal processing, not user-facing
                # Classification happens silently and routes to triage
                
                # Update state with structured classification information
                state["issue_category"] = classify_output.category
                state["issue_priority"] = classify_output.priority
                state["needs_clarification"] = False
                state["current_response"] = classify_output.response
                
                # DON'T add to conversation history - this is internal routing
                # The user doesn't need to see "I've classified this as hardware..."
            
        except ValueError as e:
            logger.error(f"Tool call parsing error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating ClassifyOutput from tool call: {e}")
            raise
        
    except Exception as e:
        logger.error(f"Error in classify_issue_node: {e}")
        # Don't mask the real error with fallback messages
        # Let the error propagate for clean error handling
        raise
    
    # Log what this node wrote to state
    log_node_complete("classify_issue", state_before, state)
    
    return state