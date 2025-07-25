"""
Classify Issue node for Support Desk workflow.

This node categorizes the IT issue into predefined categories.
"""
import logging
from copy import deepcopy
from typing import Dict, Any

from ..state import SupportDeskState
from ..prompts.classify_issue_prompt import CLASSIFICATION_PROMPT
from src.core.llm_client import client
from langgraph.config import get_stream_writer

logger = logging.getLogger(__name__)


async def classify_issue_node(state: SupportDeskState) -> SupportDeskState:
    """
    Categorize the IT issue into one of the predefined categories.
    
    This node:
    1. Analyzes the user's issue description
    2. Categorizes into: hardware, software, access, other
    3. Sets appropriate confidence levels
    4. Updates the workflow state with category information
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with category information
    """
    
    logger.info("Classify issue node processing user input")
    state = deepcopy(state)
    
    # Extract conversation history for context
    messages = state.get("messages", [])
    conversation_history = "\n".join([
        f"{msg.get('role', 'user')}: {msg.get('content', '')}" 
        for msg in messages
    ])
    
    try:
        # Get stream writer for custom streaming
        writer = get_stream_writer()
        
        # Prepare classification prompt
        classification_prompt = CLASSIFICATION_PROMPT.format(
            conversation_history=conversation_history
        )
        
        # Stream callback to emit chunks as they come in
        def stream_callback(chunk: str):
            writer({"custom_llm_chunk": chunk})
        
        # Call LLM to classify the issue
        classification_response = await client.chat_completion(
            messages=[
                {"role": "system", "content": classification_prompt}
            ],
            model="openai/gpt-4.1-mini",
            temperature=0.3,
            stream_callback=stream_callback
        )
        
        # Parse the classification response
        classification_content = classification_response.get("content", "")
        
        # Extract category from response
        # This is a simplified implementation - in a real system, we would use
        # structured output parsing or function calling
        classification_content_lower = classification_content.lower()
        if "hardware" in classification_content_lower:
            category = "hardware"
        elif "software" in classification_content_lower:
            category = "software"
        elif "access" in classification_content_lower:
            category = "access"
        else:
            category = "other"
            
        # Extract priority from response
        if "high" in classification_content_lower:
            priority = "high"
        elif "medium" in classification_content_lower:
            priority = "medium"
        else:
            priority = "low"
        
        # Update state with classification information
        state["issue_category"] = category
        state["issue_priority"] = priority
        state["current_response"] = classification_content
        
        # Append message to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": classification_content
        })
        
        logger.info(f"Issue classified as {category} with {priority} priority")
        
    except Exception as e:
        logger.error(f"Error in classify_issue_node: {e}")
        # Error response
        error_response = "I'm analyzing your issue. Moving to the next step..."
        
        # Stream the error response
        writer = get_stream_writer()
        writer({"custom_llm_chunk": error_response})
        
        state["issue_category"] = "unknown"
        state["issue_priority"] = "medium"  # Default to medium priority
        state["current_response"] = error_response
        
        # Append message to conversation history
        state["messages"].append({
            "role": "assistant",
            "content": error_response
        })
    
    return state