"""
Ticket data generator for support desk workflow.

Generates deterministic ticket data based on issue information.
"""
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any

from ..business_context import get_sla_commitment, SUPPORT_TEAMS
from ..config.company_config import COMPANY_INFO


def generate_ticket_id(issue_info: Dict[str, Any]) -> str:
    """
    Generate a deterministic ticket ID based on issue info and timestamp.
    
    Args:
        issue_info: Dictionary containing issue information
        
    Returns:
        Ticket ID in format DESK-YYYYMMDD-NNNN
    """
    # Use current date for the ID
    date_str = datetime.now().strftime("%Y%m%d")
    
    # Create a hash from issue info for uniqueness
    info_str = f"{issue_info.get('category', '')}{issue_info.get('priority', '')}{datetime.now().isoformat()}"
    hash_obj = hashlib.md5(info_str.encode())
    hash_num = int(hash_obj.hexdigest()[:8], 16) % 10000
    
    return f"DESK-{date_str}-{hash_num:04d}"


# SLA commitment function imported from business_context


def get_team_contact_info(team: str) -> Dict[str, str]:
    """
    Get contact information based on assigned team from business context.
    
    Args:
        team: Assigned support team
        
    Returns:
        Dictionary with contact details
    """
    # Get team info from business context
    if team in SUPPORT_TEAMS and "contact" in SUPPORT_TEAMS[team]:
        return SUPPORT_TEAMS[team]["contact"]
    
    # Fallback to company default contact info
    return {
        "email": COMPANY_INFO["support_email"],
        "phone": COMPANY_INFO["support_phone"],
        "portal": COMPANY_INFO["ticket_portal"]
    }


def get_next_steps(priority: str, category: str) -> str:
    """
    Generate next steps based on priority and category.
    
    Args:
        priority: Issue priority
        category: Issue category
        
    Returns:
        Next steps text
    """
    if priority.upper() == "P1":
        return "Your high-priority ticket has been escalated. A specialist will contact you within 30 minutes. Please keep your phone available."
    elif category.lower() == "hardware":
        return "A hardware technician will review your ticket and may schedule an on-site visit if needed. You'll receive an update within the SLA timeframe."
    elif category.lower() == "access":
        return "Your access request will be reviewed by the security team. You may receive additional verification requests via email."
    else:
        return "Your ticket has been assigned to the appropriate team. You'll receive updates via email as progress is made. Check the support portal for real-time status."


def generate_ticket_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate complete ticket data from workflow state.
    
    Args:
        state: Current workflow state
        
    Returns:
        Dictionary with all ticket fields populated
    """
    # Extract info from state
    category = state.get("issue_category", "other")
    priority = state.get("issue_priority", "P2")
    team = state.get("assigned_team", "L1")
    
    # Generate ticket ID
    ticket_id = generate_ticket_id({"category": category, "priority": priority})
    
    # Get SLA and contact info
    sla_text, sla_hours = get_sla_commitment(priority)
    contact_info = get_team_contact_info(team)
    
    # Calculate estimated resolution
    resolution_time = datetime.now() + timedelta(hours=sla_hours)
    
    # Get issue summary from messages - find the most substantive user message
    issue_summary = ""
    if state.get("messages"):
        user_messages = [msg.get("content", "") for msg in state["messages"] 
                        if msg.get("role") == "user" and len(msg.get("content", "").strip()) > 10]
        
        if user_messages:
            # Use the longest user message as it's likely the most descriptive
            issue_summary = max(user_messages, key=len)[:200]
        else:
            # Fallback to first user message if all are short
            for msg in state["messages"]:
                if msg.get("role") == "user":
                    issue_summary = msg.get("content", "")[:200]
                    break
    
    return {
        "ticket_id": ticket_id,
        "ticket_status": "CREATED",
        "priority": priority,
        "category": category,
        "assigned_team": team,
        "sla_commitment": sla_text,
        "issue_summary": issue_summary or "Issue details captured in ticket system",
        "next_steps": get_next_steps(priority, category),
        "support_email": contact_info.get("email", "support@company.com"),
        "support_phone": contact_info.get("phone", "1-800-SUPPORT"),
        "ticket_portal": contact_info.get("portal", "https://support.company.com"),
        "created_timestamp": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        "estimated_resolution": resolution_time.strftime("%B %d, %Y at %I:%M %p")
    }