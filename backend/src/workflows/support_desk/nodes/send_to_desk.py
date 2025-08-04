"""
Send to Desk node for Support Desk workflow - With HTML artifact support.

This node generates a brief summary and creates an HTML artifact for ticket display.
"""
import logging
from copy import deepcopy
from typing import Dict, Any

from ..state import SupportDeskState
from ..prompts.send_to_desk_prompt import FINAL_RESPONSE_PROMPT
from ..utils.state_logger import log_node_start, log_node_complete
from ..utils.ticket_generator import generate_ticket_data
from ..templates.ticket_template import generate_ticket_html
from src.core.llm_client import client
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)


async def send_to_desk_node(state: SupportDeskState) -> SupportDeskState:
    """
    Create final ticket with HTML artifact and brief summary response.
    
    This node:
    1. Generates a brief natural language summary
    2. Creates structured ticket data deterministically
    3. Streams an HTML artifact for visual ticket display
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with final ticket information and response
    """
    
    state_before = deepcopy(state)
    state = deepcopy(state)
    
    # Log what this node will read from state
    log_node_start("send_to_desk", ["issue_category", "issue_priority", "assigned_team"])
    
    # Extract ticket information from nested state
    issue_category = state.get("classification", {}).get("issue_category", "other")
    issue_priority = state.get("classification", {}).get("issue_priority", "P2")
    assigned_team = state.get("classification", {}).get("assigned_team", "L1")
    
    try:
        # Create prompt for brief summary response
        prompt = FINAL_RESPONSE_PROMPT.format(
            issue_category=issue_category,
            issue_priority=issue_priority,
            support_team=assigned_team
        )
        
        # Get stream writer for streaming
        writer = get_stream_writer()
        
        # Buffer to collect the summary response
        summary_buffer = []
        
        # Stream callback to emit chunks and collect them
        def stream_callback(chunk: str):
            writer({"custom_llm_chunk": chunk})
            summary_buffer.append(chunk)
        
        # Call LLM for brief summary only
        await client.chat_completion(
            messages=[
                {"role": "system", "content": prompt}
            ],
            model="openai/gpt-4.1",
            temperature=0.7,
            stream_callback=stream_callback,
            use_streaming=True
        )
        
        # Get the complete summary
        summary_content = "".join(summary_buffer)
        
        # Generate deterministic ticket data
        ticket_data = generate_ticket_data(state)
        
        # Generate HTML artifact
        ticket_html = generate_ticket_html(ticket_data)
        
        # Stream a newline separator
        writer({"custom_llm_chunk": "\n\n"})
        
        # Stream the HTML artifact wrapped in code blocks
        # Open WebUI will recognize this as an HTML artifact
        writer({"custom_llm_chunk": "```html\n"})
        writer({"custom_llm_chunk": ticket_html})
        writer({"custom_llm_chunk": "\n```"})
        
        # Add fixed workflow note after the artifact
        workflow_note = """

---

**Workflow complete**: Start a new conversation to test a different scenario."""
        
        writer({"custom_llm_chunk": workflow_note})
        
        # Send a completion signal to ensure everything is fully processed
        writer({"custom_llm_chunk": ""})
        
        # Update state with ticket information
        if "ticket" not in state:
            state["ticket"] = {}
        state["ticket"]["ticket_id"] = ticket_data["ticket_id"]
        state["ticket"]["ticket_status"] = ticket_data["ticket_status"]
        state["ticket"]["sla_commitment"] = ticket_data["sla_commitment"]
        state["ticket"]["next_steps"] = ticket_data["next_steps"]
        state["ticket"]["contact_information"] = {
            "email": ticket_data["support_email"],
            "phone": ticket_data["support_phone"],
            "portal": ticket_data["ticket_portal"]
        }
        state["ticket"]["estimated_resolution_time"] = ticket_data.get("estimated_resolution")
        
        # Update classification state with assigned team
        if "classification" not in state:
            state["classification"] = {}
        state["classification"]["assigned_team"] = ticket_data["assigned_team"]
        
        # Store the complete response (summary + HTML + workflow note)
        complete_response = f"{summary_content}\n\n```html\n{ticket_html}\n```{workflow_note}"
        
        # Update conversation state
        if "conversation" not in state:
            state["conversation"] = {}
        state["conversation"]["current_response"] = complete_response
        
        # Add response to conversation history
        if "messages" not in state["conversation"]:
            state["conversation"]["messages"] = []
        state["conversation"]["messages"].append({
            "role": "assistant",
            "content": complete_response
        })
        
        logger.info(f"→ ticket {ticket_data['ticket_id']} created with HTML artifact")
        logger.info("→ desk submission complete")
        
    except Exception as e:
        logger.error(f"Error in send_to_desk_node: {e}")
        # Don't mask the real error with fallback messages
        # Let the error propagate for clean error handling
        raise
    
    # Log what this node wrote to state
    log_node_complete("send_to_desk", state_before, state)
    
    return state