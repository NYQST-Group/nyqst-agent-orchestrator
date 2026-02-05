"""Always-on indexing orchestration.

This is the thin "index service" facade for the current demo stack.

Design goals:
- Treat indexing as substrate capability (no UI buttons).
- Keep strategies server-side behind profiles (IP).
- Emit runs + ledger events for auditability.
- Be swappable: today it wraps RagService (pgvector); later it can call OpenSearch/Qdrant/etc.
"""

from __future__ import annotations

import logging
from uuid import UUID

from intelli.config import settings
from intelli.db.engine import AsyncSessionLocal
from intelli.services.knowledge.rag_service import RagService
from intelli.services.runs.ledger_service import LedgerService
from intelli.services.runs.run_service import RunService

logger = logging.getLogger(__name__)


async def auto_index_manifest(
    *,
    manifest_sha256: str,
    pointer_id: UUID | None = None,
    profile: str = "docs.default",
    reason: str = "pointer_advance",
) -> UUID | None:
    """Index a manifest asynchronously (background-safe).

    Returns:
        run_id if a run was started, otherwise None (e.g., indexing disabled).
    """
    if not settings.openai_api_key:
        logger.info("Auto-index skipped (OPENAI_API_KEY not configured).")
        return None

    async with AsyncSessionLocal() as session:
        try:
            runs = RunService(session)
            ledger = LedgerService(session)
            rag = RagService(session)

            run = await runs.create_run(
                run_type="index_ingest",
                name="Index Ingest",
                config={
                    "profile": profile,
                    "reason": reason,
                    "embedding_model": settings.embedding_model,
                    "backend": "pgvector",
                    "pointer_id": str(pointer_id) if pointer_id else None,
                },
                input_manifest_sha256=manifest_sha256,
            )
            await runs.start_run(run.id)

            try:
                stats = await rag.index_manifest(
                    manifest_sha256,
                    force=False,
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
                        "profile": profile,
                    },
                )
            except Exception as exc:
                await runs.fail_run(run.id, {"type": type(exc).__name__, "message": str(exc)})
                raise

            await session.commit()
            return run.id
        except Exception:
            await session.rollback()
            raise
