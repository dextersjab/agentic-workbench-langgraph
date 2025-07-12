"""Server-Sent Events (SSE) streaming utilities for Open WebUI compatibility."""
import json
import logging
from typing import Dict, Any
from .models import ChatMessage, SystemMessage, HumanMessage, AIMessage

logger = logging.getLogger(__name__)


def _sse(data: Dict[str, Any]) -> str:
    """Format data as Server-Sent Event."""
    return f"data: {json.dumps(data)}\n\n"


def _extract_text(message) -> str:
    """Extract text content from various message types."""
    if hasattr(message, 'content'):
        return message.content
    elif isinstance(message, dict) and 'content' in message:
        return message['content']
    elif isinstance(message, str):
        return message
    else:
        logger.warning(f"Unable to extract text from message: {type(message)}")
        return ""


def _to_lc(chat_message: ChatMessage):
    """Convert OpenAI ChatMessage to LangChain message format."""
    if chat_message.role == "system":
        return SystemMessage(content=chat_message.content)
    elif chat_message.role == "user":
        return HumanMessage(content=chat_message.content)
    elif chat_message.role == "assistant":
        return AIMessage(content=chat_message.content)
    else:
        logger.warning(f"Unknown message role: {chat_message.role}")
        return HumanMessage(content=chat_message.content)


def create_sse_chunk(
    completion_id: str,
    model: str,
    created: int,
    content: str = "",
    finish_reason: str = None,
    role: str = None
) -> str:
    """Create a properly formatted SSE chunk for streaming."""
    delta = {}
    
    if content:
        delta["content"] = content
    
    if role:
        delta["role"] = role
        
    payload = {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [{
            "index": 0,
            "delta": delta,
            "finish_reason": finish_reason
        }]
    }
    
    return _sse(payload)


def create_done_chunk() -> str:
    """Create the final [DONE] SSE chunk."""
    return "data: [DONE]\n\n"


def create_error_chunk(error_message: str) -> str:
    """Create an error SSE chunk."""
    error_payload = {
        "error": {
            "message": error_message,
            "type": "internal_error"
        }
    }
    return _sse(error_payload)