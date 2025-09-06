"""OpenAI-compatible API for Open WebUI integration."""
# Import logging configuration first to set up file logging

import time
import uuid
import traceback
import logging

from .state_logger import GREY, RESET
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, APIRouter, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from .models import (
    ChatCompletionRequest,
    ModelsResponse,
    ChatCompletionResponse,
    ChatCompletionChoice,
    ChatMessage,
)
from .streaming import create_sse_chunk, create_done_chunk, create_error_chunk
from ..workflows.registry import WorkflowRegistry
from ..workflows.utils import create_workflow_initial_state

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory checkpointer for storing graph state
checkpointer = InMemorySaver()

app = FastAPI(
    title="Support Desk IT Support Agent",
    description="OpenAI-compatible API for IT support chatbot training",
    version="0.1.0",
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


def _extract_chat_id_from_headers(request: Request) -> Optional[str]:
    """Extract chat ID from Open WebUI standard header for thread persistence."""
    chat_id = request.headers.get("X-OpenWebUI-Chat-Id")
    if chat_id:
        logger.info(f"Found chat ID '{chat_id}' in header 'X-OpenWebUI-Chat-Id'")
        return chat_id

    return None


def _determine_thread_id(req: ChatCompletionRequest, request: Request) -> str:
    """Determine the thread ID for conversation state persistence."""
    # Priority 1: Chat ID from OpenWebUI headers
    chat_id = _extract_chat_id_from_headers(request)
    if chat_id:
        return f"chat-{chat_id}"

    # Priority 2: Explicit thread_id in request body
    if req.thread_id:
        return req.thread_id

    # Priority 3: Generate new thread ID (always create unique ID)
    thread_id = f"thread-{uuid.uuid4().hex}"
    logger.info(f"Generated new thread_id: {thread_id}")
    return thread_id


async def _workflow_stream(
    req: ChatCompletionRequest, workflow, thread_id: str
) -> AsyncGenerator[str, None]:
    """Stream responses from a workflow, managing interruptions."""
    logger.info(f"Streaming workflow for thread_id: {thread_id}")

    config = {"configurable": {"thread_id": thread_id}}

    # Check if there's existing state for this thread
    try:
        existing_state = await workflow.aget_state(config)
        if existing_state.values:
            # Check if this is a regenerate scenario (same messages as before)
            existing_messages = existing_state.values.get("messages", [])
            current_messages = (
                [msg.model_dump() for msg in req.messages] if req.messages else []
            )

            is_regenerate = (
                len(existing_messages) == len(current_messages)
                and existing_messages == current_messages
                and len(current_messages) > 0
            )

            if is_regenerate:
                # This is a regenerate - reset to start of workflow with same input
                logger.info(
                    f"Detected regenerate for thread {thread_id} - restarting workflow"
                )
                state = create_workflow_initial_state(req.model)
                if req.messages:
                    state["messages"] = current_messages

                # Start fresh workflow (same as new conversation)
                async for chunk in workflow.astream(
                    state, config=config, stream_mode=["custom", "updates"]
                ):
                    # Handle both tuple format (stream_type, data) and direct dictionary format
                    if isinstance(chunk, tuple) and len(chunk) == 2:
                        stream_type, stream_data = chunk
                        logger.debug(
                            f"Stream chunk received: {stream_type} -> {list(stream_data.keys()) if isinstance(stream_data, dict) else type(stream_data)}"
                        )

                        if stream_type == "custom":
                            # Handle custom LLM chunks for user-facing streaming
                            if (
                                isinstance(stream_data, dict)
                                and "custom_llm_chunk" in stream_data
                            ):
                                text = stream_data.get("custom_llm_chunk")
                                if text:
                                    yield text

                        elif stream_type == "updates":
                            # Handle node execution updates for tracking
                            if isinstance(stream_data, dict):
                                for node_name, node_updates in stream_data.items():
                                    if (
                                        node_name
                                        not in ["custom_llm_chunk", "__interrupt__"]
                                        and node_updates is not None
                                    ):
                                        logger.info(
                                            f"Node execution update - {node_name}: {type(node_updates)}"
                                        )
                                        # Tracking functionality temporarily disabled
                                        # try:
                                        #     await track_node_from_stream(node_name, node_updates, config)
                                        # except Exception as track_error:
                                        #     logger.error(f"Stream tracking failed for {node_name}: {track_error}")

                    elif isinstance(chunk, dict):
                        # Fallback for direct dictionary format (backwards compatibility)
                        logger.info(f"Direct chunk received: {list(chunk.keys())}")

                        # Check for custom LLM chunks to stream back
                        if "custom_llm_chunk" in chunk:
                            text = chunk.get("custom_llm_chunk")
                            if text:
                                yield text

                        # Handle node execution updates
                        for key, value in chunk.items():
                            if (
                                key not in ["custom_llm_chunk", "__interrupt__"]
                                and value is not None
                            ):
                                # Tracking functionality temporarily disabled
                                # try:
                                #     await track_node_from_stream(key, value, config)
                                # except Exception as track_error:
                                #     logger.error(f"Stream tracking failed for {key}: {track_error}")
                                pass

                    # Handle LangGraph interrupts (check both formats)
                    interrupt_data = None
                    if isinstance(chunk, tuple) and len(chunk) == 2:
                        _, stream_data = chunk
                        if isinstance(stream_data, dict):
                            interrupt_data = stream_data.get("__interrupt__")
                    elif isinstance(chunk, dict):
                        interrupt_data = chunk.get("__interrupt__")

                    if interrupt_data:
                        interrupts = interrupt_data
                        if interrupts:
                            # For simplicity, handle the first interrupt
                            interrupt_value = interrupts[0].value
                            logger.info(f"Workflow interrupted: {interrupt_value}")
                            return
            else:
                # True continuation - update messages in persisted state and resume
                logger.info(f"Continuing existing conversation for thread {thread_id}")
                if req.messages:
                    # Update the persisted state with new user message
                    update_state = {"messages": current_messages}
                    await workflow.aupdate_state(config, update_state)

                # Resume from interrupt point with user input
                user_input = req.messages[-1].content if req.messages else ""
                async for chunk in workflow.astream(
                    Command(resume=user_input),
                    config=config,
                    stream_mode=["custom", "updates"],
                ):
                    # Handle both tuple format (stream_type, data) and direct dictionary format
                    if isinstance(chunk, tuple) and len(chunk) == 2:
                        stream_type, stream_data = chunk
                        if stream_type == "custom" and isinstance(stream_data, dict):
                            if "custom_llm_chunk" in stream_data:
                                text = stream_data.get("custom_llm_chunk")
                                if text:
                                    yield text
                    elif isinstance(chunk, dict) and "custom_llm_chunk" in chunk:
                        text = chunk.get("custom_llm_chunk")
                        if text:
                            yield text

                    # Handle node execution updates (new tracking capability)
                    if isinstance(chunk, dict):
                        for key, value in chunk.items():
                            if (
                                key not in ["custom_llm_chunk", "__interrupt__"]
                                and value is not None
                            ):
                                # Track node execution automatically from stream (non-blocking)
                                # Tracking functionality temporarily disabled
                                # try:
                                #     await track_node_from_stream(key, value, config)
                                # except Exception as track_error:
                                #     logger.error(f"Stream tracking failed for {key}: {track_error}")
                                pass

                    # Handle LangGraph interrupt for human-in-the-loop (resume section)
                    interrupt_data = None
                    if isinstance(chunk, tuple) and len(chunk) == 2:
                        _, stream_data = chunk
                        if isinstance(stream_data, dict):
                            interrupt_data = stream_data.get("__interrupt__")
                    elif isinstance(chunk, dict):
                        interrupt_data = chunk.get("__interrupt__")

                    if interrupt_data:
                        interrupts = interrupt_data
                        if interrupts:
                            # For simplicity, handle the first interrupt
                            interrupt_value = interrupts[0].value
                            logger.info(f"Workflow interrupted: {interrupt_value}")
                            return
        else:
            # New conversation - create initial state and start fresh
            logger.info(f"Starting new conversation for thread {thread_id}")
            state = create_workflow_initial_state(req.model)
            if req.messages:
                state["messages"] = [msg.model_dump() for msg in req.messages]

            # Start new workflow with initial state
            async for chunk in workflow.astream(
                state, config=config, stream_mode=["custom", "updates"]
            ):
                # Handle both tuple format (stream_type, data) and direct dictionary format
                if isinstance(chunk, tuple) and len(chunk) == 2:
                    stream_type, stream_data = chunk
                    logger.info(
                        f"Stream chunk received: {stream_type} -> {list(stream_data.keys()) if isinstance(stream_data, dict) else type(stream_data)}"
                    )

                    if stream_type == "custom":
                        # Handle custom LLM chunks for user-facing streaming
                        if (
                            isinstance(stream_data, dict)
                            and "custom_llm_chunk" in stream_data
                        ):
                            text = stream_data.get("custom_llm_chunk")
                            if text:
                                yield text

                    elif stream_type == "updates":
                        # Handle node execution updates for tracking
                        if isinstance(stream_data, dict):
                            for node_name, node_updates in stream_data.items():
                                if (
                                    node_name
                                    not in ["custom_llm_chunk", "__interrupt__"]
                                    and node_updates is not None
                                ):
                                    logger.info(
                                        f"Node execution update - {node_name}: {type(node_updates)}"
                                    )
                                    # Tracking functionality temporarily disabled
                                    # try:
                                    #     await track_node_from_stream(node_name, node_updates, config)
                                    # except Exception as track_error:
                                    #     logger.error(f"Stream tracking failed for {node_name}: {track_error}")

                elif isinstance(chunk, dict):
                    # Fallback for direct dictionary format (backwards compatibility)
                    logger.info(f"Direct dict chunk received: {list(chunk.keys())}")

                    # Check for custom LLM chunks to stream back
                    if "custom_llm_chunk" in chunk:
                        text = chunk.get("custom_llm_chunk")
                        if text:
                            yield text

                    # Handle node execution updates
                    for key, value in chunk.items():
                        if (
                            key not in ["custom_llm_chunk", "__interrupt__"]
                            and value is not None
                        ):
                            # Tracking functionality temporarily disabled
                            # try:
                            #     await track_node_from_stream(key, value, config)
                            # except Exception as track_error:
                            #     logger.error(f"Stream tracking failed for {key}: {track_error}")
                            pass

                # Handle LangGraph interrupts (check both formats)
                interrupt_data = None
                if isinstance(chunk, tuple) and len(chunk) == 2:
                    _, stream_data = chunk
                    if isinstance(stream_data, dict):
                        interrupt_data = stream_data.get("__interrupt__")
                elif isinstance(chunk, dict):
                    interrupt_data = chunk.get("__interrupt__")

                if interrupt_data:
                    interrupts = interrupt_data
                    if interrupts:
                        # For simplicity, handle the first interrupt
                        interrupt_value = interrupts[0].value
                        logger.info(f"Workflow interrupted: {interrupt_value}")
                        return

    except Exception as e:
        # Fallback to new conversation if state retrieval fails
        logger.warning(f"Could not retrieve existing state for thread {thread_id}: {e}")
        state = create_workflow_initial_state(req.model)
        if req.messages:
            state["messages"] = [msg.model_dump() for msg in req.messages]

        # Start new workflow with initial state
        async for chunk in workflow.astream(
            state, config=config, stream_mode=["custom", "updates"]
        ):
            # Check for custom LLM chunks to stream back
            if isinstance(chunk, dict) and "custom_llm_chunk" in chunk:
                text = chunk.get("custom_llm_chunk")
                if text:
                    yield text

            # Handle node execution updates (new tracking capability)
            if isinstance(chunk, dict):
                for key, value in chunk.items():
                    if (
                        key not in ["custom_llm_chunk", "__interrupt__"]
                        and value is not None
                    ):
                        # Tracking functionality temporarily disabled
                        # Track node execution automatically from stream (non-blocking)
                        # try:
                        #     await track_node_from_stream(key, value, config)
                        # except Exception as track_error:
                        #     logger.error(f"Stream tracking failed for {key}: {track_error}")
                        pass

            # Handle LangGraph interrupt for human-in-the-loop
            if isinstance(chunk, dict) and "__interrupt__" in chunk:
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


async def _sse_generator(
    req: ChatCompletionRequest, request: Request
) -> AsyncGenerator[str, None]:
    """Generate SSE messages for streaming chat completion, managing conversation state."""
    completion_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())

    # Use the new thread ID determination logic
    thread_id = _determine_thread_id(req, request)

    logger.info(
        f"Starting chat completion - ID: {completion_id}, Model: {req.model}, Thread ID: {thread_id}"
    )

    try:
        workflow = WorkflowRegistry.get_workflow(req.model, checkpointer)
        logger.info("Got Support Desk workflow, starting stream")

        first_chunk = True
        async for text in _workflow_stream(req, workflow, thread_id):
            # Create SSE chunk
            sse_chunk = create_sse_chunk(
                completion_id=completion_id,
                model=req.model,
                created=created,
                content=text,
                role="assistant" if first_chunk else None,
                thread_id=thread_id,  # Include thread_id in response
            )

            first_chunk = False
            yield sse_chunk

        # Send final chunk if the graph hasn't been interrupted
        final_chunk = create_sse_chunk(
            completion_id=completion_id,
            model=req.model,
            created=created,
            finish_reason="stop",
            thread_id=thread_id,
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


async def _create_non_streaming_response(
    req: ChatCompletionRequest, request: Request
) -> ChatCompletionResponse:
    """Create a non-streaming chat completion response, managing conversation state."""
    completion_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())

    # Use the new thread ID determination logic
    thread_id = _determine_thread_id(req, request)

    logger.info(
        f"{GREY}Creating non-streaming chat completion - ID: {completion_id}, Model: {req.model}, Thread ID: {thread_id}{RESET}"
    )

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
                        "messages": [msg.model_dump() for msg in req.messages]
                    }
                    await workflow.aupdate_state(config, update_state)

                # Resume from interrupt point with None input
                full_response = ""
                final_state = None
                async for chunk in workflow.astream(
                    None, config=config, stream_mode=["custom", "updates"]
                ):
                    # Handle both tuple format (stream_type, data) and direct dictionary format
                    if isinstance(chunk, tuple) and len(chunk) == 2:
                        stream_type, stream_data = chunk
                        if stream_type == "custom" and isinstance(stream_data, dict):
                            if "custom_llm_chunk" in stream_data:
                                text = stream_data.get("custom_llm_chunk")
                                if text:
                                    full_response += text
                        elif stream_type == "updates" and isinstance(stream_data, dict):
                            # Handle node execution updates for tracking
                            for node_name, node_updates in stream_data.items():
                                if (
                                    node_name
                                    not in ["custom_llm_chunk", "__interrupt__"]
                                    and node_updates is not None
                                ):
                                    # Tracking functionality temporarily disabled
                                    # try:
                                    #     await track_node_from_stream(node_name, node_updates, config)
                                    # except Exception as track_error:
                                    #     logger.error(f"Stream tracking failed for {node_name}: {track_error}")
                                    pass
                    elif isinstance(chunk, dict):
                        # Fallback for direct dictionary format
                        if "custom_llm_chunk" in chunk:
                            text = chunk.get("custom_llm_chunk")
                            if text:
                                full_response += text

                        # Handle node execution updates (background tracking)
                        for key, value in chunk.items():
                            if (
                                key not in ["custom_llm_chunk", "__interrupt__"]
                                and value is not None
                            ):
                                # Track node execution automatically from stream (non-blocking)
                                # Tracking functionality temporarily disabled
                                # try:
                                #     await track_node_from_stream(key, value, config)
                                # except Exception as track_error:
                                #     logger.error(f"Stream tracking failed for {key}: {track_error}")
                                pass

                    # Update final state as we go
                    state_data = None
                    if isinstance(chunk, tuple) and len(chunk) == 2:
                        _, stream_data = chunk
                        if isinstance(stream_data, dict):
                            state_data = stream_data
                    elif isinstance(chunk, dict):
                        state_data = chunk

                    if state_data and any(
                        key for key in state_data.keys() if not key.startswith("__")
                    ):
                        final_state = state_data
            else:
                # New conversation - create initial state and start fresh
                logger.info(f"Starting new conversation for thread {thread_id}")
                state = create_workflow_initial_state(req.model)
                if req.messages:
                    state["messages"] = [msg.model_dump() for msg in req.messages]

                # Start new workflow with initial state
                full_response = ""
                final_state = None
                async for chunk in workflow.astream(
                    state, config=config, stream_mode=["custom", "updates"]
                ):
                    # Handle both tuple format (stream_type, data) and direct dictionary format
                    if isinstance(chunk, tuple) and len(chunk) == 2:
                        stream_type, stream_data = chunk
                        if stream_type == "custom" and isinstance(stream_data, dict):
                            if "custom_llm_chunk" in stream_data:
                                text = stream_data.get("custom_llm_chunk")
                                if text:
                                    full_response += text
                        elif stream_type == "updates" and isinstance(stream_data, dict):
                            # Handle node execution updates for tracking
                            for node_name, node_updates in stream_data.items():
                                if (
                                    node_name
                                    not in ["custom_llm_chunk", "__interrupt__"]
                                    and node_updates is not None
                                ):
                                    # Tracking functionality temporarily disabled
                                    # try:
                                    #     await track_node_from_stream(node_name, node_updates, config)
                                    # except Exception as track_error:
                                    #     logger.error(f"Stream tracking failed for {node_name}: {track_error}")
                                    pass
                    elif isinstance(chunk, dict):
                        # Fallback for direct dictionary format
                        if "custom_llm_chunk" in chunk:
                            text = chunk.get("custom_llm_chunk")
                            if text:
                                full_response += text

                        # Handle node execution updates (background tracking)
                        for key, value in chunk.items():
                            if (
                                key not in ["custom_llm_chunk", "__interrupt__"]
                                and value is not None
                            ):
                                # Track node execution automatically from stream (non-blocking)
                                # Tracking functionality temporarily disabled
                                # try:
                                #     await track_node_from_stream(key, value, config)
                                # except Exception as track_error:
                                #     logger.error(f"Stream tracking failed for {key}: {track_error}")
                                pass

                    # Update final state as we go
                    state_data = None
                    if isinstance(chunk, tuple) and len(chunk) == 2:
                        _, stream_data = chunk
                        if isinstance(stream_data, dict):
                            state_data = stream_data
                    elif isinstance(chunk, dict):
                        state_data = chunk

                    if state_data and any(
                        key for key in state_data.keys() if not key.startswith("__")
                    ):
                        final_state = state_data

        except Exception as e:
            # Fallback to new conversation if state retrieval fails
            logger.warning(
                f"Could not retrieve existing state for thread {thread_id}: {e}"
            )
            state = create_workflow_initial_state(req.model)
            if req.messages:
                state["messages"] = [msg.model_dump() for msg in req.messages]

            # Start new workflow with initial state
            full_response = ""
            final_state = None
            async for chunk in workflow.astream(
                state, config=config, stream_mode=["custom", "updates"]
            ):
                # Handle both tuple format (stream_type, data) and direct dictionary format
                if isinstance(chunk, tuple) and len(chunk) == 2:
                    stream_type, stream_data = chunk
                    if stream_type == "custom" and isinstance(stream_data, dict):
                        if "custom_llm_chunk" in stream_data:
                            text = stream_data.get("custom_llm_chunk")
                            if text:
                                full_response += text
                    elif stream_type == "updates" and isinstance(stream_data, dict):
                        # Handle node execution updates for tracking
                        for node_name, node_updates in stream_data.items():
                            if (
                                node_name not in ["custom_llm_chunk", "__interrupt__"]
                                and node_updates is not None
                            ):
                                # Tracking functionality temporarily disabled
                                # try:
                                #     await track_node_from_stream(node_name, node_updates, config)
                                # except Exception as track_error:
                                #     logger.error(f"Stream tracking failed for {node_name}: {track_error}")
                                pass
                elif isinstance(chunk, dict):
                    # Fallback for direct dictionary format
                    if "custom_llm_chunk" in chunk:
                        text = chunk.get("custom_llm_chunk")
                        if text:
                            full_response += text

                    # Handle node execution updates (background tracking)
                    for key, value in chunk.items():
                        if (
                            key not in ["custom_llm_chunk", "__interrupt__"]
                            and value is not None
                        ):
                            # Track node execution automatically from stream (non-blocking)
                            # Tracking functionality temporarily disabled
                            # try:
                            #     await track_node_from_stream(key, value, config)
                            # except Exception as track_error:
                            #     logger.error(f"Stream tracking failed for {key}: {track_error}")
                            pass

                # Update final state as we go
                state_data = None
                if isinstance(chunk, tuple) and len(chunk) == 2:
                    _, stream_data = chunk
                    if isinstance(stream_data, dict):
                        state_data = stream_data
                elif isinstance(chunk, dict):
                    state_data = chunk

                if state_data and any(
                    key for key in state_data.keys() if not key.startswith("__")
                ):
                    final_state = state_data

        return ChatCompletionResponse(
            id=completion_id,
            created=created,
            model=req.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=full_response),
                    finish_reason="stop"
                    if not (final_state and final_state.get("__interrupt__"))
                    else "interrupt",
                )
            ],
            usage={
                "prompt_tokens": len(str(req.messages)),
                "completion_tokens": len(full_response),
                "total_tokens": len(str(req.messages)) + len(full_response),
            },
            thread_id=thread_id,
        )

    except Exception as exc:
        logger.error(f"Error in non-streaming completion {completion_id}: {str(exc)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(exc)}",
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
async def chat_completions(chat_request: ChatCompletionRequest, request: Request):
    """Handle OpenAI-compatible chat completion requests."""
    logger.info(
        f"{GREY}Chat completion request - headers: {dict(request.headers)}{RESET}"
    )
    logger.info(f"{GREY}Chat completion request - chat_request: {chat_request}{RESET}")
    logger.info(
        f"{GREY}Chat completion request - model: {chat_request.model}, stream: {chat_request.stream}{RESET}"
    )

    if chat_request.stream:
        logger.info(f"{GREY}Starting streaming response{RESET}")
        return StreamingResponse(
            _sse_generator(chat_request, request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            },
        )
    else:
        logger.info(f"{GREY}Starting non-streaming response{RESET}")
        return await _create_non_streaming_response(chat_request, request)


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
            "models": {
                "href": "/v1/models",
                "method": "GET",
                "description": "List available AI models",
            },
            "chat": {
                "href": "/v1/chat/completions",
                "method": "POST",
                "description": "Create chat completion",
            },
            "docs": {
                "href": "/docs",
                "method": "GET",
                "description": "Interactive API documentation",
            },
        },
        "capabilities": {
            "streaming": True,
            "openai_compatible": True,
            "workflow_based": True,
            "human_in_the_loop": True,
        },
        "supported_formats": {
            "request": "application/json",
            "response": ["application/json", "text/event-stream"],
        },
    }


# Include the v1 router in the main app
app.include_router(v1_router)
