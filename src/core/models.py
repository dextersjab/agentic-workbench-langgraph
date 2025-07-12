"""OpenAI-compatible models for Open WebUI integration."""
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """OpenAI-compatible chat message."""
    role: str = Field(..., description="Message role: system, user, or assistant")
    content: str = Field(..., description="Message content")
    name: Optional[str] = Field(None, description="Optional name for the message")


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request."""
    model: str = Field(..., description="Model to use for completion")
    messages: List[ChatMessage] = Field(..., description="List of messages in conversation")
    temperature: float = Field(0.7, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    stream: bool = Field(False, description="Whether to stream responses")
    stop: Optional[Union[str, List[str]]] = Field(None, description="Stop sequences")


class ChatCompletionChoice(BaseModel):
    """OpenAI-compatible choice in completion response."""
    index: int
    message: Optional[ChatMessage] = None
    delta: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    """OpenAI-compatible chat completion response."""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Optional[Dict[str, int]] = None


class ModelInfo(BaseModel):
    """OpenAI-compatible model information."""
    id: str
    object: str = "model"
    created: int
    owned_by: str = "helphub"
    permission: List[Dict] = Field(default_factory=list)
    root: Optional[str] = None
    parent: Optional[str] = None


class ModelsResponse(BaseModel):
    """OpenAI-compatible models list response."""
    object: str = "list"
    data: List[ModelInfo]


class OpenAIError(BaseModel):
    """OpenAI-compatible error response."""
    message: str
    type: str = "invalid_request_error"
    param: Optional[str] = None
    code: Optional[str] = None


# LangChain message conversion utilities
class SystemMessage:
    """System message for LangChain compatibility."""
    def __init__(self, content: str):
        self.content = content
        self.type = "system"


class HumanMessage:
    """Human message for LangChain compatibility."""
    def __init__(self, content: str):
        self.content = content
        self.type = "human"


class AIMessage:
    """AI message for LangChain compatibility."""
    def __init__(self, content: str):
        self.content = content
        self.type = "ai"