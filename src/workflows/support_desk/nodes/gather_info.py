"""
Gather Info node for Support Desk workflow - Simplified streaming version.

This node ONLY asks questions using natural streaming. No decision making.
"""
import logging
from copy import deepcopy

from ..state import SupportDeskState
from ..utils import build_conversation_history
from ..utils.state_logger import log_node_start, log_node_complete
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
        state["max_gathering_rounds"] = 3
    
    # Build conversation history for context
    conversation_history = build_conversation_history(messages)
    
    try:
        # Create prompt for asking the next question
        missing_info_text = ", ".join(missing_categories) if missing_categories else "general details"
        
        prompt = f"""
You are an IT support agent asking a follow-up question to gather more information.

Issue Category: {issue_category}
Issue Priority: {issue_priority}
Assigned Team: {support_team}
Gathering Round: {gathering_round}
Missing Information: {missing_info_text}
Conversation History: {conversation_history}

REQUIRED INFORMATION CATEGORIES:
1. **Device/System Details**: Specific hardware/software involved, models, versions
2. **Timeline**: When did this start, frequency, patterns
3. **User Impact**: How this affects work, urgency, business impact
4. **Symptoms**: Specific error messages, behaviors, what exactly happens
5. **Context**: What user was doing when issue occurred, recent changes
6. **Environment**: User location, department, role (if relevant to issue)

For {issue_category} issues, prioritize:
- Hardware: Device models, physical symptoms, connectivity
- Software: Application versions, error messages, affected workflows  
- Access: Account names, systems, permission levels
- Network: Connection types, locations, affected devices

INSTRUCTIONS:
Ask ONE specific, targeted question to gather the most important missing information.
Focus on: {missing_info_text}

Keep the question:
- Natural and conversational
- Specific rather than vague
- Relevant to {issue_category} issues
- Helpful for the {support_team} team to resolve the issue

Examples of good questions:
- "What web browser and version are you using to access Salesforce?"
- "When did you first notice this error - was it this morning or earlier?"
- "Are other team members experiencing the same issue, or just you?"
- "What specific error message do you see when you try to log in?"

Ask your question directly - no prefixes or explanations needed.
"""
        
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
        state["gathering_round"] = gathering_round + 1
        
        # Add question to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": response_content
        })
        
        logger.info(f"→ asked question (round {gathering_round})")
        
    except Exception as e:
        logger.error(f"Error in gather_info_node: {e}")
        raise
    
    # Log what this node wrote to state
    log_node_complete("gather_info", state_before, state)
    
    # Use interrupt to pause and wait for user response
    interrupt("Waiting for user response to information gathering question")
    
    return state