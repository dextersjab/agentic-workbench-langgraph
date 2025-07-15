"""OpenAI-compatible API for Open WebUI integration."""
import json
import time
import uuid
import traceback
import logging
from typing import AsyncGenerator

from fastapi import FastAPI, APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    ChatCompletionRequest, 
    ModelsResponse, 
    ModelInfo,
    OpenAIError
)
from .streaming import create_sse_chunk, create_done_chunk, create_error_chunk, _to_lc
from ..workflows.registry import WorkflowRegistry
from ..workflows.helphub.state import create_initial_state

logger = logging.getLogger(__name__)

app = FastAPI(
    title="HelpHub IT Support Agent",
    description="OpenAI-compatible API for IT support chatbot training",
    version="0.1.0"
)

# Add CORS middleware for Open WebUI compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create v1 router
v1_router = APIRouter(prefix="/v1")


async def _helphub_stream(req: ChatCompletionRequest, workflow, state) -> AsyncGenerator[str, None]:
    """Stream responses from the HelpHub workflow."""
    logger.info("Starting HelpHub workflow stream")
    
    # Convert OpenAI messages to LangChain format
    lc_messages = [_to_lc(msg) for msg in req.messages]
    logger.info(f"Converted {len(lc_messages)} messages to LangChain format")
    
    # Set the current user input from the last message
    if req.messages:
        state["current_user_input"] = req.messages[-1].content
        state["messages"] = [msg.model_dump() for msg in req.messages]
    
    try:
        # Stream workflow execution
        async for chunk in workflow.astream(state, stream_mode="custom"):
            logger.info(f"Received chunk from workflow: {chunk}")
            if "custom_llm_chunk" in chunk:
                text = chunk["custom_llm_chunk"]
                if text:
                    logger.info(f"Yielding text: {text}")
                    yield text
    except Exception as e:
        logger.error(f"Error in workflow stream: {e}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        yield f"Error processing request: {str(e)}"


async def _sse_generator(req: ChatCompletionRequest) -> AsyncGenerator[str, None]:
    """Generate SSE messages for streaming chat completion."""
    completion_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())
    
    logger.info(f"Starting chat completion - ID: {completion_id}, Model: {req.model}")
    
    try:
        # Initialize HelpHub workflow state
        state = create_initial_state()
        workflow = WorkflowRegistry.get_workflow("helphub")
        
        logger.info("Got HelpHub workflow, starting stream")
        
        first_chunk = True
        async for text in _helphub_stream(req, workflow, state):
            logger.info(f"Received text from workflow: {text}")
            
            # Create SSE chunk
            sse_chunk = create_sse_chunk(
                completion_id=completion_id,
                model=req.model,
                created=created,
                content=text,
                role="assistant" if first_chunk else None
            )
            
            first_chunk = False
            logger.info(f"Sending SSE chunk")
            yield sse_chunk
        
        # Send final chunk
        final_chunk = create_sse_chunk(
            completion_id=completion_id,
            model=req.model,
            created=created,
            finish_reason="stop"
        )
        logger.info("Sending final SSE chunk")
        yield final_chunk
        
        # Send done signal
        logger.info("Sending [DONE] signal")
        yield create_done_chunk()

    except Exception as exc:
        logger.error(f"Error in chat completion {completion_id}: {str(exc)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        
        error_chunk = create_error_chunk(str(exc))
        yield error_chunk
        yield create_done_chunk()


@v1_router.get("/models")
async def list_models() -> ModelsResponse:
    """List available models for Open WebUI."""
    logger.info("Models list requested")
    
    models = WorkflowRegistry.get_available_models()
    return ModelsResponse(data=models)


@v1_router.options("/models")
async def models_options():
    """Handle OPTIONS request for models endpoint."""
    logger.info("Models OPTIONS request")
    return {"message": "OK"}

@v1_router.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """Handle OpenAI-compatible chat completion requests."""
    logger.info(f"Chat completion request - model: {request.model}, stream: {request.stream}")
    
    if not request.stream:
        logger.warning("Non-streaming request received - returning error")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This implementation requires stream=true for Open WebUI compatibility"
        )
    
    logger.info("Starting streaming response")
    return StreamingResponse(
        _sse_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )


# API information endpoint
@v1_router.get("/")
async def root():
    """API information with HATEOAS links."""
    return {
        "name": "HelpHub IT Support Agent API",
        "version": "1.0.0",
        "description": "OpenAI-compatible API for IT support chatbot using LangGraph workflows",
        "links": {
            "self": {"href": "/v1/", "method": "GET"},
            "models": {"href": "/v1/models", "method": "GET", "description": "List available AI models"},
            "chat": {"href": "/v1/chat/completions", "method": "POST", "description": "Create chat completion"},
            "docs": {"href": "/docs", "method": "GET", "description": "Interactive API documentation"}
        },
        "capabilities": {
            "streaming": True,
            "openai_compatible": True,
            "workflow_based": True
        },
        "supported_formats": {
            "request": "application/json",
            "response": ["application/json", "text/event-stream"]
        }
    }

# Include the v1 router in the main app
app.include_router(v1_router)
