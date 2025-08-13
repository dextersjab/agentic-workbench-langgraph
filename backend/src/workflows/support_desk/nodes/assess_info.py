"""
Assess Info node for Support Desk workflow.

This node assesses if enough information has been gathered to create a ticket.
If not, it generates targeted questions for the user.
"""
import logging
from copy import deepcopy
from typing import Literal

from ..state import SupportDeskState
from ..models.info_completeness_output import InfoCompletenessOutput
from ..prompts.has_sufficient_info_prompt import HAS_SUFFICIENT_INFO_PROMPT
from ..utils import build_conversation_history
from ..utils.state_logger import log_node_start, log_node_complete
from ..business_context import MAX_GATHERING_ROUNDS, format_required_info_categories, format_category_specific_priorities
from ..prompts.generate_question_prompt import GENERATE_QUESTION_PROMPT
from src.core.llm_client import client, pydantic_to_openai_tool, extract_tool_call_args
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)


async def assess_info_node(state: SupportDeskState) -> SupportDeskState:
    """
    Assess if enough information has been gathered to create a comprehensive ticket.
    
    This node uses tool calling for structured decision making and generates questions when needed (similar to classify_issue).
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with completeness assessment
    """
    
    state_before = deepcopy(state)
    state = deepcopy(state)
    
    # Log what this node will read from state
    log_node_start("assess_info", ["messages", "issue_category", "issue_priority", "assigned_team", "gathering_round"])
    
    # Extract relevant information from nested state
    messages = state.get("conversation", {}).get("messages", [])
    issue_category = state.get("classification", {}).get("issue_category", "other")
    issue_priority = state.get("classification", {}).get("issue_priority", "P2")
    assigned_team = state.get("classification", {}).get("assigned_team", "L1")
    gathering_round = state.get("gathering", {}).get("gathering_round", 1)
    
    # Build conversation history for context
    conversation_history = build_conversation_history(messages)
    
    # Check if we've exhausted gathering rounds
    max_rounds = MAX_GATHERING_ROUNDS
    force_proceed = gathering_round >= max_rounds
    
    # Set prompt components based on whether we need to force assessment
    if force_proceed:
        task_instruction = "Call the {tool_name} tool to assess completeness with the information available."
        additional_context = """
You MUST assess the ticket with the information available as we've reached the maximum gathering rounds.
Set needs_more_info=False as we cannot ask more questions.
"""
    else:
        task_instruction = """
If you have sufficient information to create a comprehensive ticket, call the {tool_name} tool with needs_more_info=False.

If you do NOT have sufficient information, set needs_more_info=True so that the next step can ask the user for the most critical missing detail.

As part of this agentic system, you have a maximum of {max_gathering_rounds} total rounds to gather information.
"""
        additional_context = ""
    
    # Set up the tool for structured output
    tool_name = "check_completeness"
    tools = [pydantic_to_openai_tool(InfoCompletenessOutput, tool_name)]
    
    try:
        # Create prompt for completeness assessment
        from ..kb.servicehub_policy import SERVICEHUB_SUPPORT_TICKET_POLICY
        
        prompt = HAS_SUFFICIENT_INFO_PROMPT.format(
            servicehub_support_ticket_policy=SERVICEHUB_SUPPORT_TICKET_POLICY,
            issue_category=issue_category,
            issue_priority=issue_priority,
            support_team=assigned_team,
            gathering_round=gathering_round,
            conversation_history=conversation_history,
            max_gathering_rounds=max_rounds,
            required_info_categories=format_required_info_categories(),
            category_specific_priorities=format_category_specific_priorities(issue_category),
            task_instruction=task_instruction,
            additional_context=additional_context,
            tool_name=tool_name
        )
        
        # Call LLM with tools for structured output (fast, non-streaming)
        response = await client.chat_completion(
            messages=[
                {"role": "system", "content": prompt}
            ],
            model="openai/gpt-4.1",
            temperature=0.3,
            tools=tools,
            tool_choice="required",
            use_streaming=False
        )
        
        # Extract structured output from tool call
        try:
            output_data = extract_tool_call_args(response, tool_name)
            completeness_output = InfoCompletenessOutput(**output_data)
            
            logger.info(f"→ info check: needs_more={completeness_output.needs_more_info} (conf: {completeness_output.confidence})")
            
            # Update state with assessment
            # Update gathering state
            if "gathering" not in state:
                state["gathering"] = {}
            
            # Override needs_more_info if we've hit the limit
            if force_proceed and completeness_output.needs_more_info:
                logger.info("→ force proceed: overriding needs_more_info to False")
                state["gathering"]["needs_more_info"] = False
            else:
                state["gathering"]["needs_more_info"] = completeness_output.needs_more_info
            
            state["gathering"]["info_completeness_confidence"] = completeness_output.confidence
            state["gathering"]["missing_categories"] = completeness_output.missing_categories
            state["gathering"]["user_requested_escalation"] = completeness_output.user_requested_escalation
            
            # Check if we need to generate a question (like classify_issue does)
            if completeness_output.needs_more_info and not force_proceed and not completeness_output.user_requested_escalation:
                logger.info("→ needs more info, generating question")
                
                # Generate targeted question with streaming (similar to classify_issue)
                question_prompt = GENERATE_QUESTION_PROMPT.format(
                    conversation_history=conversation_history
                )
                
                # Get stream writer for real-time streaming
                writer = get_stream_writer()
                
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
                    
                    # Add the question to messages
                    if "messages" not in state:
                        state["messages"] = []
                    state["messages"].append({
                        "role": "assistant",
                        "content": question_content
                    })
                    
                    logger.info(f"→ generated question: {question_content[:50]}...")
                    
                except Exception as e:
                    logger.error(f"Error generating info gathering question: {e}")
                    # Fallback question if generation fails
                    fallback_question = "Could you provide more details to help us create your support ticket?"
                    if "messages" not in state:
                        state["messages"] = []
                    state["messages"].append({
                        "role": "assistant", 
                        "content": fallback_question
                    })
                    logger.info("→ used fallback question due to error")
            elif completeness_output.user_requested_escalation:
                logger.info("→ user requested escalation")
            else:
                logger.info("→ sufficient info available")
            
        except ValueError as e:
            logger.error(f"Tool call parsing error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating InfoCompletenessOutput from tool call: {e}")
            raise
        
    except Exception as e:
        logger.error(f"Error in has_sufficient_info_node: {e}")
        raise
    
    # Log what this node wrote to state
    log_node_complete("assess_info", state_before, state)
    
    return state


def should_continue_to_send(state: SupportDeskState) -> Literal["proceed", "clarify", "escalate"]:
    """
    Determine if we should proceed to send to desk, clarify with more info, or escalate.
    
    Args:
        state: Current workflow state
        
    Returns:
        "escalate" if user requested escalation or force proceed
        "proceed" if sufficient info exists
        "clarify" if need to gather more
    """
    # Check for user escalation/force proceed request
    user_requested_escalation = state.get("gathering", {}).get("user_requested_escalation", False)
    if user_requested_escalation:
        logger.info("→ user requested escalation")
        return "escalate"
    
    needs_more = state.get("gathering", {}).get("needs_more_info", True)
    gathering_round = state.get("gathering", {}).get("gathering_round", 1)
    max_rounds = state.get("gathering", {}).get("max_gathering_rounds", MAX_GATHERING_ROUNDS)
    
    # Consider sufficient if we've hit max rounds or have enough info
    if gathering_round >= max_rounds:
        logger.info(f"→ max rounds reached ({max_rounds}), proceeding")
        return "proceed"
    elif not needs_more:
        logger.info("→ sufficient info collected")
        return "proceed"
    else:
        logger.info(f"→ insufficient info (round {gathering_round})")
        return "clarify"