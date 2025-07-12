"""
Priority assessment node for HelpHub workflow.

TODO for participants: Implement intelligent priority assessment based on
business impact, urgency keywords, and user context.
"""
import logging
from typing import Dict, Any
from ..state import HelpHubState
from ..prompts.priority_prompt import PRIORITY_PROMPT

logger = logging.getLogger(__name__)


def priority_node(state: HelpHubState) -> Dict[str, Any]:
    """
    Assess the priority level of the IT support ticket.
    
    This node should:
    1. Analyze urgency keywords and context
    2. Consider business impact based on user role
    3. Evaluate system-wide vs individual impact
    4. Assign P1 (Critical), P2 (High), or P3 (Medium) priority
    5. Provide reasoning for the priority assignment
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with ticket priority
        
    TODO for participants:
    - Implement LLM call using PRIORITY_PROMPT  
    - Consider user context (role, department) in priority assessment
    - Detect emergency situations requiring immediate escalation
    - Balance urgency keywords with actual business impact
    - Handle cases where priority is ambiguous
    """
    
    logger.info("Priority assessment node processing issue")
    
    user_input = state.get("current_user_input", "")
    conversation_history = state.get("messages", [])
    category = state.get("ticket_category", "unknown")
    user_context = state.get("user_context", {})
    
    # TODO: Replace this placeholder logic with LLM-based priority assessment
    # You should:
    # 1. Use PRIORITY_PROMPT to structure the assessment
    # 2. Include conversation context and user role information
    # 3. Call LLM to determine priority level and reasoning
    # 4. Parse response to extract priority and justification
    
    # Placeholder logic - participants should replace this
    user_input_lower = user_input.lower()
    
    # Check for P1 (Critical) indicators
    if any(word in user_input_lower for word in [
        "cannot", "down", "outage", "urgent", "emergency", "critical", 
        "flooding", "fire", "security breach", "system down"
    ]):
        priority = "P1"
        reasoning = "Critical issue requiring immediate attention"
        
    # Check for P2 (High) indicators  
    elif any(word in user_input_lower for word in [
        "slow", "error", "problem", "affecting", "multiple users", 
        "intermittent", "deadline", "client meeting"
    ]):
        priority = "P2"
        reasoning = "High priority issue impacting productivity"
        
    # Default to P3 (Medium)
    else:
        priority = "P3"
        reasoning = "Standard priority for general requests"
    
    # Consider category-specific priority adjustments
    if category == "access" and "locked" in user_input_lower:
        # Account lockouts are typically higher priority
        if priority == "P3":
            priority = "P2"
            reasoning = "Account lockout requires prompt resolution"
    
    # Update state
    state["ticket_priority"] = priority
    
    logger.info(f"Assigned priority: {priority} - {reasoning}")
    
    # Set response for streaming
    response = f"I've assessed this as a {priority} priority issue. {reasoning}"
    state["current_response"] = response
    state["custom_llm_chunk"] = response
    
    return state


def escalate_emergency(state: HelpHubState) -> bool:
    """
    Determine if this is an emergency requiring immediate escalation.
    
    TODO for participants:
    - Implement emergency detection logic
    - Define what constitutes an emergency (security, safety, critical systems)
    - Create escalation procedures for different emergency types
    
    Returns:
        True if emergency escalation is needed
    """
    
    user_input = state.get("current_user_input", "").lower()
    
    # TODO: Implement comprehensive emergency detection
    emergency_keywords = [
        "fire", "flooding", "security breach", "data loss", 
        "server room", "power outage", "gas leak"
    ]
    
    return any(keyword in user_input for keyword in emergency_keywords)