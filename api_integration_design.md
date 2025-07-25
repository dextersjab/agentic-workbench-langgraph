# API Integration Design for IT Service Desk

## Overview

This document outlines the necessary updates to integrate the new Support Desk workflow with the existing API. The API provides an OpenAI-compatible interface that allows the workflow to be used with Open WebUI and other compatible clients.

## Current API Implementation

The current API is implemented in `src/core/api.py` and provides the following functionality:

1. OpenAI-compatible chat completions endpoint
2. Models listing endpoint
3. Streaming and non-streaming response handling
4. Error handling and logging

## Required Updates

To integrate the Support Desk workflow, we need to make the following updates:

1. Update imports to use the Support Desk state
2. Update workflow initialization to use the Support Desk workflow
3. Update any references to HelpHub in the API documentation

## Detailed Implementation

Here's the detailed implementation of the updated API:

```python
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
    OpenAIError,
    ChatCompletionResponse,
    ChatCompletionChoice,
    ChatMessage
)
from .streaming import create_sse_chunk, create_done_chunk, create_error_chunk, _to_lc
from ..workflows.registry import WorkflowRegistry
from ..workflows.support_desk.state import create_initial_state

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Support Desk IT Service Agent",
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


async def _support_desk_stream(req: ChatCompletionRequest, workflow, state) -> AsyncGenerator[str, None]:
    """Stream responses from the Support Desk workflow."""
    logger.info("Starting Support Desk workflow stream")
    
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
        # Initialize Support Desk workflow state
        state = create_initial_state()
        workflow = WorkflowRegistry.get_workflow("support_desk")
        
        logger.info("Got Support Desk workflow, starting stream")
        
        first_chunk = True
        async for text in _support_desk_stream(req, workflow, state):
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


async def _create_non_streaming_response(req: ChatCompletionRequest) -> ChatCompletionResponse:
    """Create a non-streaming chat completion response."""
    completion_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())
    
    logger.info(f"Creating non-streaming chat completion - ID: {completion_id}, Model: {req.model}")
    
    try:
        # Initialize Support Desk workflow state
        state = create_initial_state()
        workflow = WorkflowRegistry.get_workflow("support_desk")
        
        # Convert OpenAI messages to LangChain format
        lc_messages = [_to_lc(msg) for msg in req.messages]
        
        # Set the current user input from the last message
        if req.messages:
            state["current_user_input"] = req.messages[-1].content
            state["messages"] = [msg.model_dump() for msg in req.messages]
        
        # Collect all workflow output
        full_response = ""
        async for chunk in workflow.astream(state, stream_mode="custom"):
            if "custom_llm_chunk" in chunk:
                text = chunk["custom_llm_chunk"]
                if text:
                    full_response += text
        
        # Create the response
        return ChatCompletionResponse(
            id=completion_id,
            created=created,
            model=req.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=full_response),
                    finish_reason="stop"
                )
            ],
            usage={
                "prompt_tokens": len(str(req.messages)),
                "completion_tokens": len(full_response),
                "total_tokens": len(str(req.messages)) + len(full_response)
            }
        )
        
    except Exception as exc:
        logger.error(f"Error in non-streaming completion {completion_id}: {str(exc)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(exc)}"
        )


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
    logger.info(f"Chat completion request - request: {request}")
    logger.info(f"Chat completion request - model: {request.model}, stream: {request.stream}")
    
    if request.stream:
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
    else:
        logger.info("Starting non-streaming response")
        return await _create_non_streaming_response(request)


# API information endpoint
@v1_router.get("/")
async def root():
    """API information with HATEOAS links."""
    return {
        "name": "Support Desk IT Service Agent API",
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
```

## Key Changes

### 1. Updated Imports

The imports have been updated to use the Support Desk state:

```python
from ..workflows.support_desk.state import create_initial_state
```

This replaces the previous import from HelpHub.

### 2. Updated Function Names

Function names have been updated to reflect the new workflow:

```python
async def _support_desk_stream(req: ChatCompletionRequest, workflow, state) -> AsyncGenerator[str, None]:
    """Stream responses from the Support Desk workflow."""
```

This replaces the previous `_helphub_stream` function.

### 3. Updated Workflow Initialization

The workflow initialization has been updated to use the Support Desk workflow:

```python
# Initialize Support Desk workflow state
state = create_initial_state()
workflow = WorkflowRegistry.get_workflow("support_desk")
```

This ensures that the API uses the new workflow.

### 4. Updated API Documentation

The API documentation has been updated to reflect the new workflow:

```python
app = FastAPI(
    title="Support Desk IT Service Agent",
    description="OpenAI-compatible API for IT support chatbot training",
    version="0.1.0"
)
```

And:

```python
return {
    "name": "Support Desk IT Service Agent API",
    "version": "1.0.0",
    "description": "OpenAI-compatible API for IT support chatbot using LangGraph workflows",
    # ...
}
```

## Integration Flow

When a client makes a request to the API:

1. The API initializes the Support Desk workflow state
2. It retrieves the Support Desk workflow from the registry
3. It processes the user input and passes it to the workflow
4. The workflow executes, potentially looping through the clarification node
5. The API streams the response back to the client

This flow is the same as before, but now it uses the Support Desk workflow instead of HelpHub.

## Educational Value

This API integration design demonstrates several important concepts:

1. **OpenAI Compatibility**: How to create an API that follows the OpenAI standard
2. **Streaming Responses**: How to stream responses from a workflow
3. **Error Handling**: How to handle errors in an API context
4. **Workflow Integration**: How to integrate a workflow with an API

Students will learn:
- How to integrate LangGraph workflows with FastAPI
- How to create OpenAI-compatible APIs
- How to implement streaming responses
- How to handle errors in an API context

## Implementation Notes

The API integration will be implemented in `src/core/api.py` and will include:

1. Updated imports
2. Updated function names
3. Updated workflow initialization
4. Updated API documentation

These changes will ensure that the API uses the Support Desk workflow instead of HelpHub, completing the integration as specified in the requirements.