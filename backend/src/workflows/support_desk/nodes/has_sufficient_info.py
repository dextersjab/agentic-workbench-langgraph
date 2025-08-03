"""
Has Sufficient Info node for Support Desk workflow.

This node determines if enough information has been gathered to create a ticket.
"""
import logging
from copy import deepcopy

from ..state import SupportDeskState
from ..models.info_completeness_output import InfoCompletenessOutput
from ..prompts.has_sufficient_info_prompt import HAS_SUFFICIENT_INFO_PROMPT
from ..utils import build_conversation_history
from ..utils.state_logger import log_node_start, log_node_complete
from ..business_context import MAX_GATHERING_ROUNDS
from src.core.llm_client import client, pydantic_to_openai_tool, extract_tool_call_args

logger = logging.getLogger(__name__)


async def has_sufficient_info_node(state: SupportDeskState) -> SupportDeskState:
    """
    Determine if enough information has been gathered to create a comprehensive ticket.
    
    This node uses tool calling for fast, structured decision making (similar to classify_issue).
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with completeness assessment
    """
    
    state_before = deepcopy(state)
    state = deepcopy(state)
    
    # Log what this node will read from state
    log_node_start("has_sufficient_info", ["messages", "issue_category", "issue_priority", "assigned_team", "gathering_round"])
    
    # Extract relevant information
    messages = state.get("messages", [])
    issue_category = state.get("issue_category", "other")
    issue_priority = state.get("issue_priority", "P2")
    assigned_team = state.get("assigned_team", "L1")
    gathering_round = state.get("gathering_round", 1)
    
    # Build conversation history for context
    conversation_history = build_conversation_history(messages)
    
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
            max_gathering_rounds=MAX_GATHERING_ROUNDS,
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
            state["needs_more_info"] = completeness_output.needs_more_info
            state["info_completeness_confidence"] = completeness_output.confidence
            state["missing_categories"] = completeness_output.missing_categories
            # state["current_response"] = completeness_output.response
            
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
    log_node_complete("has_sufficient_info", state_before, state)
    
    return state


def has_sufficient_info(state: SupportDeskState) -> bool:
    """
    Determine if we have sufficient information to proceed to ticket creation.
    
    Args:
        state: Current workflow state
        
    Returns:
        True if sufficient info exists, False if need to gather more
    """
    needs_more = state.get("needs_more_info", True)
    gathering_round = state.get("gathering_round", 1)
    max_rounds = state.get("max_gathering_rounds", MAX_GATHERING_ROUNDS)
    
    # Consider sufficient if we've hit max rounds or have enough info
    if gathering_round >= max_rounds:
        logger.info(f"→ max rounds reached ({max_rounds}), considering sufficient")
        return True
    elif not needs_more:
        logger.info("→ sufficient info collected")
        return True
    else:
        logger.info(f"→ insufficient info (round {gathering_round})")
        return False