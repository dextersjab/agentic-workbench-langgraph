"""OpenAI-compatible API for Open WebUI integration."""
# Import logging configuration first to set up file logging
from . import logging_config

import json
import time
import uuid
import traceback
import logging

from src.workflows.support_desk.utils.state_logger import GREY, RESET
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Interrupt, Command

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

# In-memory checkpointer for storing graph state
checkpointer = InMemorySaver()

app = FastAPI(
    title="Support Desk IT Support Agent",
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


async def _support_desk_stream(req: ChatCompletionRequest, workflow, thread_id: str) -> AsyncGenerator[str, None]:
    """Stream responses from the Support Desk workflow, managing interruptions."""
    logger.info(f"Streaming Support Desk workflow for thread_id: {thread_id}")
    
    config = {"configurable": {"thread_id": thread_id}}
    
    # Check if there's existing state for this thread
    try:
        existing_state = await workflow.aget_state(config)
        if existing_state.values:
            # Continuing conversation - update messages in persisted state and resume
            logger.info(f"Continuing existing conversation for thread {thread_id}")
            if req.messages:
                # Update the persisted state with new user message
                update_state = {
                    "current_user_input": req.messages[-1].content,
                    "messages": [msg.model_dump() for msg in req.messages]
                }
                await workflow.aupdate_state(config, update_state)
            
            # Resume from interrupt point with user input
            user_input = req.messages[-1].content if req.messages else ""
            async for chunk in workflow.astream(Command(resume=user_input), config=config, stream_mode="custom"):
                logger.info(f"Received chunk from workflow: {chunk}")
                
                # Check for custom LLM chunks to stream back
                if "custom_llm_chunk" in chunk:
                    text = chunk.get("custom_llm_chunk")
                    if text:
                        logger.info(f"Yielding text: {text}")
                        yield text
                
                # Handle LangGraph interrupt for human-in-the-loop
                if "__interrupt__" in chunk:
                    interrupts = chunk.get("__interrupt__", [])
                    if interrupts:
                        # For simplicity, handle the first interrupt
                        interrupt_value = interrupts[0].value
                        logger.info(f"Workflow interrupted: {interrupt_value}")
                        return
        else:
            # New conversation - create initial state and start fresh
            logger.info(f"Starting new conversation for thread {thread_id}")
            state = create_initial_state()
            if req.messages:
                state["current_user_input"] = req.messages[-1].content
                state["messages"] = [msg.model_dump() for msg in req.messages]
            
            # Start new workflow with initial state
            async for chunk in workflow.astream(state, config=config, stream_mode="custom"):
                logger.info(f"Received chunk from workflow: {chunk}")
                
                # Check for custom LLM chunks to stream back
                if "custom_llm_chunk" in chunk:
                    text = chunk.get("custom_llm_chunk")
                    if text:
                        logger.info(f"Yielding text: {text}")
                        yield text
                
                # Handle LangGraph interrupt for human-in-the-loop
                if "__interrupt__" in chunk:
                    interrupts = chunk.get("__interrupt__", [])
                    if interrupts:
                        # For simplicity, handle the first interrupt
                        interrupt_value = interrupts[0].value
                        logger.info(f"Workflow interrupted: {interrupt_value}")
                        return
                        
    except Exception as e:
        # Fallback to new conversation if state retrieval fails
        logger.warning(f"Could not retrieve existing state for thread {thread_id}: {e}")
        state = create_initial_state()
        if req.messages:
            state["current_user_input"] = req.messages[-1].content
            state["messages"] = [msg.model_dump() for msg in req.messages]
        
        # Start new workflow with initial state
        async for chunk in workflow.astream(state, config=config, stream_mode="custom"):
            logger.info(f"Received chunk from workflow: {chunk}")
            
            # Check for custom LLM chunks to stream back
            if "custom_llm_chunk" in chunk:
                text = chunk.get("custom_llm_chunk")
                if text:
                    logger.info(f"Yielding text: {text}")
                    yield text
            
            # Handle LangGraph interrupt for human-in-the-loop
            if "__interrupt__" in chunk:
                interrupts = chunk.get("__interrupt__", [])
                if interrupts:
                    # For simplicity, handle the first interrupt
                    interrupt_value = interrupts[0].value
                    logger.info(f"Received interrupt with value: {interrupt_value}")
                    if interrupt_value:
                        logger.info(f"Yielding interrupt text: {interrupt_value}")
                        yield interrupt_value
                        # Stop streaming after an interrupt
                        return

    except Exception as e:
        logger.error(f"Error in workflow stream for thread {thread_id}: {e}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        yield f"Error processing request: {str(e)}"


async def _sse_generator(req: ChatCompletionRequest) -> AsyncGenerator[str, None]:
    """Generate SSE messages for streaming chat completion, managing conversation state."""
    completion_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())
    
    # Use thread_id from request if provided, otherwise use default thread for consistency
    thread_id = req.thread_id or "default-thread"
    logger.info(f"Starting chat completion - ID: {completion_id}, Model: {req.model}, Thread ID: {thread_id}")
    
    try:
        workflow = WorkflowRegistry.get_workflow(req.model, checkpointer)
        logger.info("Got Support Desk workflow, starting stream")
        
        first_chunk = True
        async for text in _support_desk_stream(req, workflow, thread_id):
            logger.info(f"Received text from workflow: {text}")
            
            # Create SSE chunk
            sse_chunk = create_sse_chunk(
                completion_id=completion_id,
                model=req.model,
                created=created,
                content=text,
                role="assistant" if first_chunk else None,
                thread_id=thread_id  # Include thread_id in response
            )
            
            first_chunk = False
            logger.info(f"Sending SSE chunk")
            yield sse_chunk
        
        # Send final chunk if the graph hasn't been interrupted
        final_chunk = create_sse_chunk(
            completion_id=completion_id,
            model=req.model,
            created=created,
            finish_reason="stop",
            thread_id=thread_id
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
    """Create a non-streaming chat completion response, managing conversation state."""
    completion_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())
    
    # Use thread_id from request if provided, otherwise use default thread for consistency
    thread_id = req.thread_id or "default-thread"
    logger.info(f"{GREY}Creating non-streaming chat completion - ID: {completion_id}, Model: {req.model}, Thread ID: {thread_id}{RESET}")
    
    try:
        workflow = WorkflowRegistry.get_workflow(req.model, checkpointer)
        
        config = {"configurable": {"thread_id": thread_id}}
        
        # Check if there's existing state for this thread
        try:
            existing_state = await workflow.aget_state(config)
            if existing_state.values:
                # Continuing conversation - update messages in persisted state and resume
                logger.info(f"Continuing existing conversation for thread {thread_id}")
                if req.messages:
                    # Update the persisted state with new user message
                    update_state = {
                        "current_user_input": req.messages[-1].content,
                        "messages": [msg.model_dump() for msg in req.messages]
                    }
                    await workflow.aupdate_state(config, update_state)
                
                # Resume from interrupt point with None input
                full_response = ""
                final_state = None
                async for chunk in workflow.astream(None, config=config, stream_mode="custom"):
                    if "custom_llm_chunk" in chunk:
                        text = chunk.get("custom_llm_chunk")
                        if text:
                            full_response += text
                    
                    # Update final state as we go
                    if hasattr(chunk, 'get') and any(key for key in chunk.keys() if not key.startswith('__')):
                        final_state = chunk
            else:
                # New conversation - create initial state and start fresh
                logger.info(f"Starting new conversation for thread {thread_id}")
                state = create_initial_state()
                if req.messages:
                    state["current_user_input"] = req.messages[-1].content
                    state["messages"] = [msg.model_dump() for msg in req.messages]
                
                # Start new workflow with initial state
                full_response = ""
                final_state = None
                async for chunk in workflow.astream(state, config=config, stream_mode="custom"):
                    if "custom_llm_chunk" in chunk:
                        text = chunk.get("custom_llm_chunk")
                        if text:
                            full_response += text
                    
                    # Update final state as we go
                    if hasattr(chunk, 'get') and any(key for key in chunk.keys() if not key.startswith('__')):
                        final_state = chunk
                        
        except Exception as e:
            # Fallback to new conversation if state retrieval fails
            logger.warning(f"Could not retrieve existing state for thread {thread_id}: {e}")
            state = create_initial_state()
            if req.messages:
                state["current_user_input"] = req.messages[-1].content
                state["messages"] = [msg.model_dump() for msg in req.messages]
            
            # Start new workflow with initial state
            full_response = ""
            final_state = None
            async for chunk in workflow.astream(state, config=config, stream_mode="custom"):
                if "custom_llm_chunk" in chunk:
                    text = chunk.get("custom_llm_chunk")
                    if text:
                        full_response += text
                
                # Update final state as we go
                if hasattr(chunk, 'get') and any(key for key in chunk.keys() if not key.startswith('__')):
                    final_state = chunk

        return ChatCompletionResponse(
            id=completion_id,
            created=created,
            model=req.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=full_response),
                    finish_reason="stop" if not (final_state and final_state.get("__interrupt__")) else "interrupt"
                )
            ],
            usage={
                "prompt_tokens": len(str(req.messages)),
                "completion_tokens": len(full_response),
                "total_tokens": len(str(req.messages)) + len(full_response)
            },
            thread_id=thread_id
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
    logger.info(f"{GREY}Chat completion request - request: {request}{RESET}")
    logger.info(f"{GREY}Chat completion request - model: {request.model}, stream: {request.stream}{RESET}")
    
    if request.stream:
        logger.info(f"{GREY}Starting streaming response{RESET}")
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
        logger.info(f"{GREY}Starting non-streaming response{RESET}")
        return await _create_non_streaming_response(request)


# API information endpoint
@v1_router.get("/")
async def root():
    """API information with HATEOAS links."""
    return {
        "name": "Support Desk IT Support Agent API",
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
            "workflow_based": True,
            "human_in_the_loop": True
        },
        "supported_formats": {
            "request": "application/json",
            "response": ["application/json", "text/event-stream"]
        }
    }

# Include the v1 router in the main app
app.include_router(v1_router)
