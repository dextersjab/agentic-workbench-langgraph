"""
Gather Info node for Support Desk workflow - Simplified streaming version.

This node ONLY asks questions using natural streaming. No decision making.
"""
import logging
from copy import deepcopy

from ..state import SupportDeskState
from ..utils import build_conversation_history
from ..utils.state_logger import log_node_start, log_node_complete
from ..constants import MAX_GATHERING_ROUNDS
from ..kb.servicehub_policy import SERVICEHUB_SUPPORT_TICKET_POLICY
from src.core.llm_client import client
from langgraph.config import get_stream_writer
from langgraph.types import interrupt

logger = logging.getLogger(__name__)


async def gather_info_node(state: SupportDeskState) -> SupportDeskState:
    """
    Ask one targeted question to gather more information.
    
    This node ONLY asks questions using natural streaming. 
    Decision making about completeness is handled by check_info_completeness_node.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with question asked to user
    """
    
    state_before = deepcopy(state)
    state = deepcopy(state)
    
    # Log what this node will read from state
    log_node_start("gather_info", ["messages", "issue_category", "issue_priority", "support_team", "gathering_round", "missing_categories"])
    
    # Extract relevant information
    messages = state.get("messages", [])
    issue_category = state.get("issue_category", "other")
    issue_priority = state.get("issue_priority", "P2")
    support_team = state.get("support_team", "L1")
    gathering_round = state.get("gathering_round", 1)
    missing_categories = state.get("missing_categories", ["device_details", "timeline"])
    
    # Initialize max_gathering_rounds if not set
    if "max_gathering_rounds" not in state:
        state["max_gathering_rounds"] = MAX_GATHERING_ROUNDS
    
    # Build conversation history for context
    conversation_history = build_conversation_history(messages)
    
    try:
        # Import the proper prompt
        from ..prompts.gather_info_prompt import INFO_GATHERING_PROMPT
        
        # Create prompt for asking the next question
        missing_info_text = ", ".join(missing_categories) if missing_categories else "general details"
        
        prompt = INFO_GATHERING_PROMPT.format(
            servicehub_support_ticket_policy=SERVICEHUB_SUPPORT_TICKET_POLICY,
            issue_category=issue_category,
            issue_priority=issue_priority,
            support_team=support_team,
            conversation_history=conversation_history,
            tool_name="gather_info_analysis",
            gathering_round=gathering_round,
            missing_info_text=missing_info_text
        )
        
        # Get stream writer for streaming
        writer = get_stream_writer()
        
        # Stream callback to emit chunks as they come in
        def stream_callback(chunk: str):
            writer({"custom_llm_chunk": chunk})
        
        # Call LLM with regular streaming for natural user experience
        response = await client.chat_completion(
            messages=[
                {"role": "system", "content": prompt}
            ],
            model="openai/gpt-4.1",
            temperature=0.3,
            stream_callback=stream_callback,
            use_streaming=True
        )
        
        # Use the streamed response directly
        response_content = response.get("content", "")
        
        # Update state with the question
        state["current_response"] = response_content
        new_round = gathering_round + 1
        state["gathering_round"] = new_round
        
        # Add question to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": response_content
        })
        
        logger.info(f"→ asked question (moving to round {new_round})")
        
    except Exception as e:
        logger.error(f"Error in gather_info_node: {e}")
        raise
    
    # Log what this node wrote to state
    log_node_complete("gather_info", state_before, state)
    
    # Use interrupt to pause and wait for user response (outside try-except)
    interrupt("Waiting for user response to information gathering question")
    
    return state