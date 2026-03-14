"""Agent chat API endpoints.

Provides streaming chat with the research assistant agent.
Uses Vercel AI SDK compatible streaming format (per ADR-005).
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession

from intelli.agents.adapters import LangGraphToAISDKAdapter
from intelli.agents.graphs.research_assistant import ResearchAssistantGraph, ResearchState
from intelli.agents.observability import get_langfuse_handler
from intelli.api.dependencies import get_session
from intelli.api.middleware.auth import AuthContext
from intelli.config import settings
from intelli.db.checkpointer import get_checkpointer
from intelli.schemas.agent import AgentChatRequest
from intelli.services.conversation_service import ConversationService
from intelli.services.runs.ledger_service import LedgerService
from intelli.services.runs.run_service import RunService
from intelli.services.substrate.pointer_service import PointerService
from intelli.services.usage.pricing import PRICE_TABLE_VERSION, estimate_cost_micros

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat")
async def agent_chat(
    ctx: AuthContext,
    data: AgentChatRequest,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Stream a chat response from the research assistant agent.

    This endpoint returns a streaming response in Vercel AI SDK format,
    compatible with the useChat hook from @ai-sdk/react.

    The stream uses the AI SDK Data Stream Protocol:
    - "0:" prefix for text chunks
    - "2:" prefix for data chunks (sources, tool calls)
    - "d:" prefix for done signal

    If conversation_id is provided, the conversation is resumed (multi-turn).
    Otherwise, a new conversation is created. The conversation_id is returned
    in the X-Conversation-Id response header.
    """
    pointers = PointerService(session)
    runs = RunService(session)
    ledger = LedgerService(session)
    conv_service = ConversationService(session)

    manifest_sha256 = data.manifest_sha256
    if data.pointer_id:
        try:
            pointer = await pointers.get_pointer_by_id(data.pointer_id)
            manifest_sha256 = pointer.manifest_sha256
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pointer {data.pointer_id} not found",
            )

    if not manifest_sha256:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No document context provided. Please specify pointer_id or manifest_sha256.",
        )

    # Auth is required - tenant_id and user_id are guaranteed by AuthContext
    if not ctx.tenant_id or not ctx.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    tenant_id: UUID = ctx.tenant_id
    user_id: UUID = ctx.user_id

    # Extract the latest user message (needed for auto-titling and graph input)
    last_user_msg = None
    for msg in reversed(data.messages):
        if msg.role == "user":
            last_user_msg = msg
            break

    if not last_user_msg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user message provided.",
        )

    # Resolve or create conversation (auth is now required)
    conversation_id = data.conversation_id
    if conversation_id:
        # Resume existing conversation
        conv = await conv_service.conv_repo.get_by_id(conversation_id)
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found",
            )
    else:
        # Create new conversation
        # Auto-title from first user message (truncated to 100 chars)
        auto_title = last_user_msg.content[:100] if last_user_msg else None
        conv = await conv_service.create(
            tenant_id=tenant_id,
            user_id=user_id,
            module="research",
            title=auto_title,
            session_id=data.session_id,
            # Scope to the pointer if provided, so conversations are filtered by notebook
            scope_type="pointer" if data.pointer_id else "user",
            scope_id=str(data.pointer_id) if data.pointer_id else None,
            config_snapshot={
                "model": settings.chat_model,
                "pointer_id": str(data.pointer_id) if data.pointer_id else None,
                "manifest_sha256": manifest_sha256,
            },
        )
        conversation_id = conv.id

    run = await runs.create_run(
        run_type="agent_chat",
        name="Research Assistant Chat",
        config={
            "model": settings.chat_model,
            "pointer_id": str(data.pointer_id) if data.pointer_id else None,
            "conversation_id": str(conversation_id),
        },
        input_manifest_sha256=manifest_sha256,
        session_id=data.session_id,
        created_by=user_id,
    )
    await runs.start_run(run.id)

    # Save user message to application tables (only if conversation exists)
    user_msg = None
    if conversation_id:
        user_msg = await conv_service.save_message(
            conversation_id=conversation_id,
            role="user",
            content=last_user_msg.content,
        )

    initial_state = ResearchState(
        messages=[HumanMessage(content=last_user_msg.content)],
        manifest_sha256=manifest_sha256,
        context_pointer_id=str(data.pointer_id) if data.pointer_id else None,
        run_id=run.id,
    )

    # Build graph with checkpointer for multi-turn (if available)
    try:
        checkpointer = await get_checkpointer()
    except Exception:
        checkpointer = None
    graph = ResearchAssistantGraph(session=session, ledger=ledger, checkpointer=checkpointer)
    adapter = LangGraphToAISDKAdapter(ledger=ledger, run_id=run.id)

    # LangGraph config with thread_id for checkpointer (use run_id as fallback)
    thread_id = str(conversation_id) if conversation_id else str(run.id)

    # Add Langfuse callback for observability (if enabled)
    langfuse_handler = get_langfuse_handler(
        session_id=str(data.session_id) if data.session_id else str(run.id),
        user_id=str(user_id),
    )
    callbacks = [langfuse_handler] if langfuse_handler else []

    lg_config = {
        "configurable": {"thread_id": thread_id},
        "callbacks": callbacks,
    }

    async def generate():
        try:
            # Emit conversation_id and run_id as message-metadata so the frontend can capture it
            if conversation_id:
                yield adapter._sse(
                    {
                        "type": "message-metadata",
                        "messageMetadata": {
                            "conversationId": str(conversation_id),
                            "runId": str(run.id),
                        },
                    }
                )

            # Stream all events from the graph (adapter no longer emits finish event)
            async for chunk in adapter.convert_events_stream(
                graph.astream_events(initial_state, config=lg_config)
            ):
                yield chunk

            # Get token usage and latency from adapter
            token_usage = adapter.get_token_usage()
            latency_ms = adapter.get_latency_ms()
            input_tokens = int(token_usage.get("input_tokens", 0) or 0)
            output_tokens = int(token_usage.get("output_tokens", 0) or 0)
            cost_micros = estimate_cost_micros(
                settings.chat_model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
            if input_tokens or output_tokens or cost_micros:
                await runs.record_token_usage(
                    run.id,
                    model=settings.chat_model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost_micros=cost_micros,
                )

            # Save assistant message from accumulated adapter text
            assistant_content = adapter._accumulated_text
            assistant_msg = None
            if assistant_content and conversation_id:
                assistant_msg = await conv_service.save_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=assistant_content,
                    model_id=settings.chat_model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost_micros=cost_micros,
                    latency_ms=latency_ms,
                )

            # Build metadata dict to include in finish event
            metadata = {}
            if user_msg and assistant_msg:
                metadata = {
                    "conversationId": str(conversation_id),
                    "runId": str(run.id),
                    "userMessageId": str(user_msg.id),
                    "assistantMessageId": str(assistant_msg.id),
                    "outputTokens": output_tokens,
                    "inputTokens": input_tokens,
                    "costMicros": cost_micros,
                    "latencyMs": latency_ms,
                    "priceTableVersion": PRICE_TABLE_VERSION,
                }

            # Emit finish event with metadata attached
            # Per AI SDK v5+ spec, metadata should be in messageMetadata field of finish event
            # SSE format: event: message\ndata: {"type":"finish","messageMetadata":{...}}
            yield adapter._format_done(metadata if metadata else None)

            await runs.complete_run(
                run.id,
                result={"status": "completed", "conversation_id": str(conversation_id)},
            )
        except Exception as e:
            await runs.fail_run(run.id, {"type": type(e).__name__, "message": str(e)})
            yield adapter._format_data_chunk({"type": "error", "message": str(e)})
            yield adapter._format_done()

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Run-Id": str(run.id),
        "X-Vercel-AI-UI-Message-Stream": "v1",
        "X-Accel-Buffering": "no",
    }
    if conversation_id:
        headers["X-Conversation-Id"] = str(conversation_id)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers=headers,
    )
