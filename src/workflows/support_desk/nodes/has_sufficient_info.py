"""
Has Sufficient Info node for Support Desk workflow.

This node determines if enough information has been gathered to create a ticket.
"""
import logging
from copy import deepcopy

from ..state import SupportDeskState
from ..models.info_completeness_output import InfoCompletenessOutput
from ..utils import build_conversation_history
from ..utils.state_logger import log_node_start, log_node_complete
from ..constants import MAX_GATHERING_ROUNDS
from ..kb.servicehub_policy import SERVICEHUB_SUPPORT_TICKET_POLICY
from src.core.llm_client import client
from src.core.schema_utils import pydantic_to_openai_tool, extract_tool_call_args

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
    log_node_start("has_sufficient_info", ["messages", "issue_category", "issue_priority", "support_team", "gathering_round"])
    
    # Extract relevant information
    messages = state.get("messages", [])
    issue_category = state.get("issue_category", "other")
    issue_priority = state.get("issue_priority", "P2")
    support_team = state.get("support_team", "L1")
    gathering_round = state.get("gathering_round", 1)
    
    # Check last user message for escalation phrases
    last_user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            last_user_message = msg.get("content", "").lower()
            break
    
    escalation_phrases = [
        "just raise the ticket",
        "connect me to a human",
        "send me to a human", 
        "human please",
        "stop asking",
        "no more questions",
        "raise the ticket"
    ]
    
    user_requested_escalation = any(phrase in last_user_message for phrase in escalation_phrases)
    
    # Build conversation history for context
    conversation_history = build_conversation_history(messages)
    
    # Set up the tool for structured output
    tool_name = "check_completeness"
    tools = [pydantic_to_openai_tool(InfoCompletenessOutput, tool_name)]
    
    try:
        # Create prompt for completeness assessment
        prompt = f"""
You are a ServiceHub IT support analyst assessing if enough information has been gathered to create a comprehensive support ticket.

{SERVICEHUB_SUPPORT_TICKET_POLICY}

CURRENT TICKET CONTEXT:
Issue Category: {issue_category}
Issue Priority: {issue_priority}
Assigned Team: {support_team}
Gathering Round: {gathering_round}
User Requested Escalation: {user_requested_escalation}
Last User Message: {last_user_message}
Conversation History: {conversation_history}

IMPORTANT: If User Requested Escalation is True, you MUST set needs_more_info=False and proceed with ticket creation.

REQUIRED INFORMATION CATEGORIES:
1. **Device/System Details**: Specific hardware/software involved, models, versions
2. **Timeline**: When did this start, frequency, patterns
3. **User Impact**: How this affects work, urgency, business impact
4. **Symptoms**: Specific error messages, behaviors, what exactly happens
5. **Context**: What user was doing when issue occurred, recent changes
6. **Environment**: User location, department, role (if relevant to issue)

For {issue_category} issues in ServiceHub's environment, prioritize:
- Hardware: Device models, physical symptoms, connectivity (Dell/Lenovo equipment)
- Software: Application versions, error messages, affected workflows (ServiceHub Portal, Dynamics 365, Salesforce CRM, Azure AD)
- Access: Account names, systems, permission levels (consider department-specific procedures)
- Network: Connection types, locations, affected devices (London HQ, Manchester, Edinburgh, remote workers)

ASSESSMENT CRITERIA:
- Set needs_more_info=True if critical information is missing for ServiceHub's procedures
- Set needs_more_info=False if you have enough to create a meaningful ticket following ServiceHub standards
- After {MAX_GATHERING_ROUNDS} rounds of gathering, be more lenient (colleagues get fatigued)
- Consider issue priority and ServiceHub SLAs - P1 issues may need less detail to start resolution
- Consider ServiceHub-specific requirements (location, department, systems)

EXAMPLES OF SUFFICIENT INFORMATION FOR SERVICEHUB:
- "Sales colleagues can't access Salesforce CRM - getting 'service unavailable' error. This is blocking our quarterly deal closure calls."
  → Usually sufficient: specific ServiceHub system, error type, business impact

- "I can't log in to the ServiceHub Portal" + "started this morning" + "error says password invalid" + "working from Manchester office"
  → Sufficient: system, timeline, specific error, location

EXAMPLES NEEDING MORE INFO:
- "Something is broken" → needs what ServiceHub system, what's happening
- "The Portal is slow" → needs specific performance issue, when it started, which Portal function

Use the {tool_name} tool to assess completeness for ServiceHub procedures.
"""
        
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
            state["current_response"] = completeness_output.response
            
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
    
    # Check for user escalation in messages
    messages = state.get("messages", [])
    last_user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            last_user_message = msg.get("content", "").lower()
            break
    
    escalation_phrases = [
        "just raise the ticket",
        "connect me to a human",
        "send me to a human", 
        "human please",
        "stop asking",
        "no more questions",
        "raise the ticket"
    ]
    
    user_requested_escalation = any(phrase in last_user_message for phrase in escalation_phrases)
    
    # Consider sufficient if user requested escalation, hit max rounds, or have enough info
    if user_requested_escalation:
        logger.info("→ user requested escalation, proceeding to ticket creation")
        return True
    elif gathering_round >= max_rounds:
        logger.info(f"→ max rounds reached ({max_rounds}), considering sufficient")
        return True
    elif not needs_more:
        logger.info("→ sufficient info collected")
        return True
    else:
        logger.info(f"→ insufficient info (round {gathering_round})")
        return False