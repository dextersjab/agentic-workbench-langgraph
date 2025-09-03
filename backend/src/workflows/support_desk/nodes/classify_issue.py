"""
Classify Issue node for Support Desk workflow.

This node categorises the IT issue into predefined categories.
"""
import json
import logging
from copy import deepcopy
from typing import Dict, Any, Literal
from pathlib import Path

from ..state import SupportDeskState
from ..models.classify_output import ClassifyOutput
from ..prompts.classify_issue_prompt import format_classification_prompt
from ..prompts.generate_question_prompt import GENERATE_QUESTION_PROMPT
from ..utils import build_conversation_history, load_ontologies, format_categories_for_prompt, format_priorities_for_prompt
from src.core.state_logger import log_node_start, log_node_complete
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
        prompt = format_classification_prompt(
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
            
            # Log classification results
            category = classify_output.category
            priority = classify_output.priority
            logger.info(f"→ {str(category)} | {str(priority)} (conf: {classify_output.confidence})")
            
            # Always update classification state
            if "classification" not in state:
                state["classification"] = {}
            state["classification"]["issue_category"] = classify_output.category
            state["classification"]["issue_priority"] = classify_output.priority
            state["classification"]["user_requested_escalation"] = classify_output.user_requested_escalation
            
            # Update gathering state for clarification needs
            if "gathering" not in state:
                state["gathering"] = {}
            
            # Check if clarification is needed (unless we've hit the limit)
            if classify_output.needs_clarification and not force_proceed:
                logger.info("→ needs clarification")
                state["gathering"]["needs_clarification"] = True
                
                # Make separate LLM call to generate clarifying question with real streaming
                logger.info("→ generating clarifying question")
                
                question_prompt = GENERATE_QUESTION_PROMPT.format(
                    conversation_history=conversation_history
                )
                
                # Buffer to collect the question
                question_buffer = []
                
                # Stream callback to emit chunks and collect them
                def stream_callback(chunk: str):
                    writer({"custom_llm_chunk": chunk})
                    question_buffer.append(chunk)
                
                try:
                    # Call LLM with streaming for question generation
                    await client.chat_completion(
                        messages=[
                            {"role": "system", "content": question_prompt}
                        ],
                        model="openai/gpt-4.1",
                        temperature=0.7,  # Slightly more creative for question generation
                        stream_callback=stream_callback,
                        use_streaming=True
                    )
                    
                    # Get the complete question
                    question_content = "".join(question_buffer)
                    
                    # Add the clarifying question to messages
                    if "messages" not in state:
                        state["messages"] = []
                    state["messages"].append({
                        "role": "assistant",
                        "content": question_content
                    })
                    
                    logger.info(f"→ generated question: {question_content[:50]}...")
                    
                except Exception as e:
                    logger.error(f"Error generating clarifying question: {e}")
                    # Fallback question if generation fails
                    fallback_question = "Could you provide more details about your IT support request?"
                    if "messages" not in state:
                        state["messages"] = []
                    state["messages"].append({
                        "role": "assistant", 
                        "content": fallback_question
                    })
                    logger.info("→ used fallback question due to error")
                
            elif classify_output.user_requested_escalation:
                logger.info("→ user requested escalation")
                state["gathering"]["needs_clarification"] = False
                # Will route directly to send_to_desk
            else:
                logger.info("→ classification complete")
                state["gathering"]["needs_clarification"] = False
                # Will route to triage
            
            # Add the tool call response to messages for context
            if "messages" not in state:
                state["messages"] = []
            state["messages"].append({
                "role": "assistant",
                "content": response
            })
            
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


def should_continue_to_route(state: SupportDeskState) -> Literal["clarify", "proceed", "escalate"]:
    """
    Determine routing from classification: clarify, proceed, or escalate.
    
    Args:
        state: Current workflow state
        
    Returns:
        "escalate" if user requested escalation
        "clarify" if needs clarification or missing category/priority
        "proceed" if classification is complete and ready to proceed
    """
    # Check for escalation request
    user_requested_escalation = state.get("classification", {}).get("user_requested_escalation", False)
    if user_requested_escalation:
        logger.info("→ user requested escalation")
        return "escalate"
    
    # Check if we need clarification
    needs_clarification = state.get("gathering", {}).get("needs_clarification", False)
    category = state.get("classification", {}).get("issue_category")
    priority = state.get("classification", {}).get("issue_priority")
    
    if needs_clarification or category is None or priority is None:
        logger.info("→ needs clarification")
        return "clarify"
    else:
        logger.info("→ ready to proceed")
        return "proceed"