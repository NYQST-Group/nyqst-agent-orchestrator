"""RAG API endpoints (demo-grade).

Provides:
- POST /rag/index : chunk + embed artifacts in a manifest/pointer
- POST /rag/ask   : retrieve chunks + generate an answer with citations
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from intelli.api.dependencies import get_session
from intelli.api.middleware.auth import AuthContext
from intelli.config import settings
from intelli.schemas.rag import (
    RagAskRequest,
    RagAskResponse,
    RagIndexRequest,
    RagIndexResponse,
    RagSource,
)
from intelli.services.knowledge.rag_service import RagService
from intelli.services.runs.ledger_service import LedgerService
from intelli.services.runs.run_service import RunService
from intelli.services.substrate.pointer_service import PointerService
from intelli.services.usage.pricing import PRICE_TABLE_VERSION

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/index", response_model=RagIndexResponse)
async def index_rag(
    ctx: AuthContext,
    data: RagIndexRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Index all artifacts referenced by a manifest or pointer."""
    pointers = PointerService(session)
    runs = RunService(session)
    ledger = LedgerService(session)
    rag = RagService(session)

    manifest_sha256 = data.manifest_sha256
    if data.pointer_id:
        pointer = await pointers.get_pointer_by_id(data.pointer_id)
        manifest_sha256 = pointer.manifest_sha256

    if not manifest_sha256:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No manifest to index (pointer is empty).",
        )

    run = await runs.create_run(
        run_type="rag_index",
        name="RAG Index",
        config={"force": data.force, "embedding_model": settings.embedding_model},
        input_manifest_sha256=manifest_sha256,
        created_by=ctx.user_id,
    )
    await runs.start_run(run.id)

    try:
        stats = await rag.index_manifest(
            manifest_sha256,
            force=data.force,
            run_id=run.id,
            ledger=ledger,
        )
        await runs.complete_run(
            run.id,
            result={
                "manifest_sha256": stats.manifest_sha256,
                "artifacts_total": stats.artifacts_total,
                "artifacts_indexed": stats.artifacts_indexed,
                "artifacts_skipped": stats.artifacts_skipped,
                "chunks_created": stats.chunks_created,
                "embedding_model": settings.embedding_model,
                "price_table_version": PRICE_TABLE_VERSION,
            },
        )
    except ValueError as exc:
        await runs.fail_run(run.id, {"type": type(exc).__name__, "message": str(exc)})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        await runs.fail_run(run.id, {"type": type(exc).__name__, "message": str(exc)})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return RagIndexResponse(
        run_id=run.id,
        manifest_sha256=stats.manifest_sha256,
        embedding_model=settings.embedding_model,
        artifacts_total=stats.artifacts_total,
        artifacts_indexed=stats.artifacts_indexed,
        artifacts_skipped=stats.artifacts_skipped,
        chunks_created=stats.chunks_created,
    )


@router.post("/ask", response_model=RagAskResponse)
async def ask_rag(
    ctx: AuthContext,
    data: RagAskRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Ask a question scoped to a manifest/pointer."""
    pointers = PointerService(session)
    runs = RunService(session)
    ledger = LedgerService(session)
    rag = RagService(session)

    manifest_sha256 = data.manifest_sha256
    if data.pointer_id:
        pointer = await pointers.get_pointer_by_id(data.pointer_id)
        manifest_sha256 = pointer.manifest_sha256

    if not manifest_sha256:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No manifest to query (pointer is empty).",
        )

    run = await runs.create_run(
        run_type="rag_ask",
        name="RAG Ask",
        config={"top_k": data.top_k, "model": settings.chat_model},
        input_manifest_sha256=manifest_sha256,
        created_by=ctx.user_id,
    )
    await runs.start_run(run.id)

    try:
        answer, retrieved = await rag.answer(
            manifest_sha256,
            data.question,
            top_k=data.top_k,
            run_id=run.id,
            ledger=ledger,
        )
        await runs.complete_run(
            run.id,
            result={
                "question": data.question,
                "top_k": data.top_k,
                "sources": len(retrieved),
                "model": settings.chat_model,
                "price_table_version": PRICE_TABLE_VERSION,
            },
        )
    except ValueError as exc:
        await runs.fail_run(run.id, {"type": type(exc).__name__, "message": str(exc)})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        await runs.fail_run(run.id, {"type": type(exc).__name__, "message": str(exc)})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    sources = [
        RagSource(
            chunk_id=r.chunk_id,
            score=r.score,
            artifact_sha256=r.artifact_sha256,
            path=(r.path_hint or None),
            chunk_index=r.chunk_index,
            content=r.content,
        )
        for r in retrieved
    ]

    return RagAskResponse(
        run_id=run.id,
        model=settings.chat_model,
        answer=answer,
        sources=sources,
    )
