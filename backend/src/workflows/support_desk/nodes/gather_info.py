"""
Gather Info node for Support Desk workflow - Two-stage real streaming version.

This node analyzes if more information is needed and asks targeted questions when required.
Uses a two-stage approach:
1. Structured output for decision-making (needs_more_info, missing_categories, etc.)
2. Real-time streaming LLM call for question generation when needed
"""
import json
import logging
from copy import deepcopy

from ..state import SupportDeskState
from ..models.gather_info_output import GatherInfoOutput, GatherInfoDecision
from ..prompts.gather_info_prompt import INFO_GATHERING_PROMPT, QUESTION_GENERATION_PROMPT
from ..utils import build_conversation_history
from ..utils.state_logger import log_node_start, log_node_complete
from ..business_context import MAX_GATHERING_ROUNDS
from ..kb.servicehub_policy import SERVICEHUB_SUPPORT_TICKET_POLICY
from src.core.llm_client import client
from src.core.schema_utils import pydantic_to_json_schema
from langgraph.config import get_stream_writer
from langgraph.types import interrupt
from langgraph.errors import GraphInterrupt

logger = logging.getLogger(__name__)


async def gather_info_node(state: SupportDeskState) -> SupportDeskState:
    """
    Analyze if more information is needed and ask targeted questions.
    
    Uses tool calls for decision making, streams questions when needed.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with targeted question if needed
    """
    
    state_before = deepcopy(state)
    state = deepcopy(state)
    
    # Log what this node will read from state
    log_node_start("gather_info", ["messages", "issue_category", "issue_priority", "assigned_team", "gathering_round", "missing_categories"])
    
    messages = state.get("conversation", {}).get("messages", [])
    issue_category = state.get("classification", {}).get("issue_category", "other")
    issue_priority = state.get("classification", {}).get("issue_priority", "P2")
    assigned_team = state.get("classification", {}).get("assigned_team", "L1")
    gathering_round = state.get("gathering", {}).get("gathering_round", 1)
    missing_categories = state.get("gathering", {}).get("missing_categories", [])
    
    # Initialize max_gathering_rounds if not set
    if "gathering" not in state:
        state["gathering"] = {}
    if "max_gathering_rounds" not in state["gathering"]:
        state["gathering"]["max_gathering_rounds"] = MAX_GATHERING_ROUNDS
    
    # Check if we're resuming (last message is our question)
    last_msg = messages[-1] if messages else None
    if last_msg and last_msg.get("role") == "assistant" and gathering_round > 1:
        # This is a resume - the interrupt will immediately return the user's response
        logger.info("→ resuming from interrupt")
        interrupt("Waiting for user response to information gathering")
        
        # Now we can safely increment the round
        new_round = gathering_round + 1
        state["gathering"]["gathering_round"] = new_round
        logger.info(f"→ received user response, now at round {new_round}")
        
        # Log and return the updated state
        log_node_complete("gather_info", state_before, state)
        return state
    
    # Build conversation history for context
    conversation_history = build_conversation_history(messages)
    
    # Set up response format for decision-only structured output
    schema_name = "gather_info_decision"
    response_format = pydantic_to_json_schema(GatherInfoDecision, schema_name)
    
    try:
        # Create prompt for information gathering analysis
        missing_info_text = ", ".join(missing_categories) if missing_categories else "general details"
        
        prompt = INFO_GATHERING_PROMPT.format(
            servicehub_support_ticket_policy=SERVICEHUB_SUPPORT_TICKET_POLICY,
            issue_category=issue_category,
            issue_priority=issue_priority,
            support_team=assigned_team,
            conversation_history=conversation_history,
            tool_name=schema_name,
            gathering_round=gathering_round,
            missing_info_text=missing_info_text
        )
        
        # Call LLM with structured output format (non-streaming for decision)
        response = await client.chat_completion(
            messages=[
                {"role": "system", "content": prompt}
            ],
            model="openai/gpt-4.1",
            temperature=0.3,
            response_format=response_format,
            use_streaming=False
        )
        
        # Parse JSON response and validate with Pydantic
        try:
            output_data = json.loads(response["content"])
            decision_output = GatherInfoDecision(**output_data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse structured output: {e}")
            logger.error(f"Response content: {response.get('content', 'No content')}")
            raise
        
        logger.info(f"→ needs_more_info: {decision_output.needs_more_info}, gathering_complete: {decision_output.gathering_complete}")
        
        # Handle based on decision
        if decision_output.gathering_complete or not decision_output.needs_more_info:
            # Sufficient info - proceed silently without streaming
            logger.info("→ sufficient information, proceeding to next step")
            # Update missing categories in state
            state["gathering"]["missing_categories"] = decision_output.missing_categories
            # Don't stream anything or add to messages
            # Just return to continue workflow
            log_node_complete("gather_info", state_before, state)
            return state
        
        # Need more info - generate and stream the question in real-time
        logger.info("→ generating and streaming information gathering question")
        
        # Prepare question generation prompt
        missing_info_text = ", ".join(decision_output.missing_categories) if decision_output.missing_categories else "general details"
        question_prompt = QUESTION_GENERATION_PROMPT.format(
            servicehub_support_ticket_policy=SERVICEHUB_SUPPORT_TICKET_POLICY,
            issue_category=issue_category,
            issue_priority=issue_priority,
            support_team=assigned_team,
            conversation_history=conversation_history,
            gathering_round=gathering_round,
            missing_info_text=missing_info_text
        )
        
        # Set up streaming callback
        writer = get_stream_writer()
        streamed_content = []
        
        def stream_callback(chunk: str):
            writer({"custom_llm_chunk": chunk})
            streamed_content.append(chunk)
        
        # Generate question with real-time streaming
        question_response = await client.chat_completion(
            messages=[
                {"role": "system", "content": question_prompt}
            ],
            model="openai/gpt-4.1",
            temperature=0.7,
            stream_callback=stream_callback,
            use_streaming=True
        )
        
        # Get the full streamed question
        streamed_question = "".join(streamed_content)
        
        # Add streamed question to conversation
        if streamed_question:
            if "conversation" not in state:
                state["conversation"] = {}
            if "messages" not in state["conversation"]:
                state["conversation"]["messages"] = []
            state["conversation"]["messages"].append({
                "role": "assistant",
                "content": streamed_question
            })
            
            # Update state with the response
            state["conversation"]["current_response"] = streamed_question
        
        # Update missing categories from decision
        state["gathering"]["missing_categories"] = decision_output.missing_categories
        
        # Log what this node wrote to state before interrupt
        log_node_complete("gather_info", state_before, state)
        
        # Interrupt and wait for user response
        # When resumed, this will return the user's input
        interrupt("Waiting for user response to information gathering")
        
        # This code only executes on resume
        # Now we can safely increment the round
        new_round = gathering_round + 1
        state["gathering"]["gathering_round"] = new_round
        logger.info(f"→ received user response, incremented to round {new_round}")
        
        return state
        
    except GraphInterrupt:
        # Re-raise interrupts - these are expected LangGraph behavior
        raise
    except Exception as e:
        logger.error(f"Error in gather_info_node: {e}")
        # Don't mask the real error with fallback messages
        # Let the error propagate for clean error handling
        raise