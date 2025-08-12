"""
Classify Issue node for Support Desk workflow.

This node categorises the IT issue into predefined categories.
"""
import json
import logging
from copy import deepcopy
from typing import Dict, Any
from pathlib import Path

from ..state import SupportDeskState
from ..models.classify_output import ClassifyOutput
from ..prompts.classify_issue_prompt import CLASSIFICATION_PROMPT
from ..utils import build_conversation_history, load_ontologies, format_categories_for_prompt, format_priorities_for_prompt
from ..utils.state_logger import log_node_start, log_node_complete
from ..kb.servicehub_policy import SERVICEHUB_SUPPORT_TICKET_POLICY
from src.core.llm_client import client, pydantic_to_openai_tool, extract_tool_call_args
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)




async def classify_issue_node(state: SupportDeskState) -> SupportDeskState:
    """
    Categorise the IT issue using structured outputs.
    
    This node uses tool calling to generate structured ClassifyOutput responses
    for reliable issue categorisation and priority assignment.
    
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
    clarification_attempts = state.get("gathering", {}).get("clarification_attempts", 0)
    max_attempts = state.get("gathering", {}).get("max_clarification_attempts", 3)
    force_proceed = clarification_attempts >= max_attempts
    
    # Set prompt components based on whether we need to force classification
    if force_proceed:
        task_instruction = "Call the {tool_name} tool with the combination of category and priority."
        additional_context = """
You MUST classify the issue according to your best guess with the information available.
"""
    else:
        task_instruction = """
If you have sufficient information to confidently classify this ticket, call the {tool_name} tool with the combination of category and priority.

If you do NOT have sufficient information, set clarification=True so that the next step can directly ask the user by asking for the most information-dense missing detail.

As part of this agentic system, you have a maximum of {max_clarification_attempts} total attempts to ask the user for information, which we limit to keep the user experience as pleasant as possible.
"""
        additional_context = ""
    
    # Set up the tool for structured output
    tool_name = "classify_issue"
    tools = [pydantic_to_openai_tool(ClassifyOutput, tool_name)]
    
    try:
        # Load ontologies (now includes required_info)
        categories, priorities, _ = load_ontologies()
        
        # Format ontologies for prompt
        issue_categories = format_categories_for_prompt(categories)
        priority_levels = format_priorities_for_prompt(priorities)
        
        logger.debug(f"formatted {issue_categories=}")
        logger.debug(f"formatted {priority_levels=}")
        # Create prompt with tool calling instruction
        prompt = CLASSIFICATION_PROMPT.format(
            conversation_history=conversation_history,
            tool_name=tool_name,
            clarification_attempts=clarification_attempts,
            max_clarification_attempts=max_attempts,
            task_instruction=task_instruction,
            additional_context=additional_context,
            issue_categories=issue_categories,
            priority_levels=priority_levels,
            servicehub_support_ticket_policy=SERVICEHUB_SUPPORT_TICKET_POLICY
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
        
        # Extract category and priority from tool call
        try:
            output_data = extract_tool_call_args(response, tool_name)
            classify_output = ClassifyOutput(**output_data)
            
            logger.info(f"→ {classify_output.category}/{classify_output.priority} (conf: {classify_output.confidence})")
            
            # Check if clarification is needed (unless we've hit the limit)
            if classify_output.needs_clarification and not force_proceed:
                logger.info("→ needs clarification")
                
                # Update gathering state
                if "gathering" not in state:
                    state["gathering"] = {}
                state["gathering"]["needs_clarification"] = True
                
                # Add clarifying question to conversation
                if "messages" not in state:
                    state["messages"] = []
                state["messages"].append({
                    "role": "assistant",
                    "content": classify_output.response
                })
            else:
                logger.info("→ classification complete")
                
                # DON'T stream - this is internal processing, not user-facing
                # Classification happens silently and routes to triage
                
                # Update state with structured classification information
                if "classification" not in state:
                    state["classification"] = {}
                state["classification"]["issue_category"] = classify_output.category
                state["classification"]["issue_priority"] = classify_output.priority
                
                if "gathering" not in state:
                    state["gathering"] = {}
                state["gathering"]["needs_clarification"] = False
                # state["current_response"] = classify_output.response
                
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