"""Minimal RAG service (index + ask) for demo workflows.

This intentionally stays lightweight:
- Indexes artifacts in a manifest into chunk embeddings (Postgres + pgvector)
- Answers questions scoped to a manifest using retrieved chunks + an LLM

It is not a full KnowledgeBase/Corpus implementation yet.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from io import BytesIO
from time import perf_counter
from uuid import UUID

from docling.document_converter import DocumentConverter
from docling_core.types.io import DocumentStream
from openai import AsyncOpenAI
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from intelli.config import settings
from intelli.db.models.rag import RagChunk
from intelli.db.models.substrate import Artifact
from intelli.services.runs.ledger_service import LedgerService
from intelli.services.substrate.artifact_service import ArtifactService
from intelli.services.substrate.manifest_service import ManifestService


@dataclass(frozen=True)
class RagIndexStats:
    manifest_sha256: str
    artifacts_total: int
    artifacts_indexed: int
    artifacts_skipped: int
    chunks_created: int


@dataclass(frozen=True)
class RagRetrievedChunk:
    chunk: RagChunk
    distance: float


def _chunk_text(text: str, max_chars: int = 2000, overlap: int = 200) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []

    max_chars = max(200, max_chars)
    overlap = max(0, min(overlap, max_chars // 2))

    # Collapse excessive whitespace for more stable chunks.
    normalized = " ".join(text.split())

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(len(normalized), start + max_chars)

        # Prefer breaking at a whitespace boundary near the end.
        if end < len(normalized):
            boundary = normalized.rfind(" ", start + max_chars - 200, end)
            if boundary > start + 200:
                end = boundary

        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(normalized):
            break
        start = max(0, end - overlap)

    return chunks


class RagService:
    """RAG service scoped to artifact manifests."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.artifacts = ArtifactService(session)
        self.manifests = ManifestService(session)
        self._converter: DocumentConverter | None = None

    def _get_converter(self) -> DocumentConverter:
        if self._converter is None:
            self._converter = DocumentConverter()
        return self._converter

    def _get_openai(self) -> AsyncOpenAI:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        return AsyncOpenAI(api_key=settings.openai_api_key)

    async def _extract_text(
        self,
        artifact: Artifact,
        content: bytes,
        *,
        run_id: UUID | None = None,
        ledger: LedgerService | None = None,
        path_hint: str | None = None,
    ) -> str:
        # Fast-path for text/json.
        if artifact.media_type.startswith("text/") or artifact.media_type in {
            "application/json",
            "application/x-ndjson",
        }:
            try:
                return content.decode("utf-8")
            except UnicodeDecodeError:
                return content.decode("utf-8", errors="ignore")

        # Docling conversion for documents (pdf/docx/html/etc.).
        name = artifact.filename or f"{artifact.sha256}.bin"
        stream = DocumentStream(name=name, stream=BytesIO(content))
        converter = self._get_converter()

        tool_name = "docling.convert"
        start = perf_counter()
        if ledger and run_id:
            await ledger.log_tool_call_start(
                run_id=run_id,
                tool_name=tool_name,
                tool_version=None,
                arguments={
                    "name": name,
                    "media_type": artifact.media_type,
                    "path_hint": path_hint,
                    "size_bytes": artifact.size_bytes,
                },
            )

        try:
            result = await asyncio.to_thread(converter.convert, stream)
            text = result.document.export_to_text()
        except Exception as exc:
            if ledger and run_id:
                await ledger.log_tool_call_complete(
                    run_id=run_id,
                    tool_name=tool_name,
                    result={"ok": False, "error": {"type": type(exc).__name__, "message": str(exc)}},
                    duration_ms=int((perf_counter() - start) * 1000),
                )
            raise
        else:
            if ledger and run_id:
                await ledger.log_tool_call_complete(
                    run_id=run_id,
                    tool_name=tool_name,
                    result={"ok": True},
                    duration_ms=int((perf_counter() - start) * 1000),
                )

        return text

    async def _embed_texts(
        self,
        texts: list[str],
        *,
        run_id: UUID | None = None,
        ledger: LedgerService | None = None,
    ) -> list[list[float]]:
        client = self._get_openai()
        tool_name = "openai.embeddings"
        start = perf_counter()

        if ledger and run_id:
            await ledger.log_tool_call_start(
                run_id=run_id,
                tool_name=tool_name,
                tool_version=None,
                arguments={
                    "model": settings.embedding_model,
                    "items": len(texts),
                },
            )

        resp = await client.embeddings.create(
            model=settings.embedding_model,
            input=texts,
        )

        if ledger and run_id:
            await ledger.log_tool_call_complete(
                run_id=run_id,
                tool_name=tool_name,
                result={"items": len(resp.data)},
                duration_ms=int((perf_counter() - start) * 1000),
            )

        return [d.embedding for d in resp.data]

    async def _artifact_already_indexed(self, artifact_sha256: str) -> bool:
        stmt = (
            select(func.count())
            .select_from(RagChunk)
            .where(RagChunk.artifact_sha256 == artifact_sha256)
            .where(RagChunk.embedding_model == settings.embedding_model)
        )
        result = await self.session.execute(stmt)
        return (result.scalar_one() or 0) > 0

    async def _delete_artifact_chunks(self, artifact_sha256: str) -> None:
        stmt = (
            delete(RagChunk)
            .where(RagChunk.artifact_sha256 == artifact_sha256)
            .where(RagChunk.embedding_model == settings.embedding_model)
        )
        await self.session.execute(stmt)

    async def index_manifest(
        self,
        manifest_sha256: str,
        *,
        force: bool = False,
        run_id: UUID | None = None,
        ledger: LedgerService | None = None,
    ) -> RagIndexStats:
        entries = await self.manifests.get_entries(manifest_sha256)

        artifact_to_path: dict[str, str] = {}
        for e in entries:
            artifact_to_path.setdefault(e.artifact_sha256, e.path)

        artifacts_total = len(artifact_to_path)
        artifacts_indexed = 0
        artifacts_skipped = 0
        chunks_created = 0

        for artifact_sha256, path_hint in artifact_to_path.items():
            if not force and await self._artifact_already_indexed(artifact_sha256):
                artifacts_skipped += 1
                continue

            if force:
                await self._delete_artifact_chunks(artifact_sha256)

            if ledger and run_id:
                await ledger.log_step_start(
                    run_id=run_id,
                    step_name="index_artifact",
                    input_data={"artifact_sha256": artifact_sha256, "path": path_hint},
                )

            artifact = await self.artifacts.get_artifact(artifact_sha256)
            content = await self.artifacts.get_content(artifact_sha256)

            text = await self._extract_text(
                artifact,
                content,
                run_id=run_id,
                ledger=ledger,
                path_hint=path_hint,
            )

            chunks = _chunk_text(text)
            if not chunks:
                artifacts_skipped += 1
                if ledger and run_id:
                    await ledger.log_step_complete(
                        run_id=run_id,
                        step_name="index_artifact",
                        output_data={"skipped": True, "reason": "no_text"},
                        success=True,
                    )
                continue

            # Embed in small batches to keep request sizes reasonable.
            embeddings: list[list[float]] = []
            batch_size = 64
            for i in range(0, len(chunks), batch_size):
                embeddings.extend(
                    await self._embed_texts(
                        chunks[i : i + batch_size],
                        run_id=run_id,
                        ledger=ledger,
                    )
                )

            for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings, strict=True)):
                self.session.add(
                    RagChunk(
                        artifact_sha256=artifact_sha256,
                        chunk_index=idx,
                        content=chunk_text,
                        meta={"path": path_hint},
                        embedding_model=settings.embedding_model,
                        embedding_dimensions=len(embedding),
                        embedding=embedding,
                    )
                )

            artifacts_indexed += 1
            chunks_created += len(chunks)

            if ledger and run_id:
                await ledger.log_step_complete(
                    run_id=run_id,
                    step_name="index_artifact",
                    output_data={"chunks": len(chunks), "embedding_model": settings.embedding_model},
                    success=True,
                )

        return RagIndexStats(
            manifest_sha256=manifest_sha256,
            artifacts_total=artifacts_total,
            artifacts_indexed=artifacts_indexed,
            artifacts_skipped=artifacts_skipped,
            chunks_created=chunks_created,
        )

    async def retrieve(
        self,
        manifest_sha256: str,
        query: str,
        *,
        top_k: int = 8,
    ) -> list[RagRetrievedChunk]:
        entries = await self.manifests.get_entries(manifest_sha256)
        artifact_shas = sorted({e.artifact_sha256 for e in entries})
        if not artifact_shas:
            return []

        query_embedding = (await self._embed_texts([query]))[0]
        distance = RagChunk.embedding.cosine_distance(query_embedding).label("distance")

        stmt = (
            select(RagChunk, distance)
            .where(RagChunk.embedding_model == settings.embedding_model)
            .where(RagChunk.artifact_sha256.in_(artifact_shas))
            .order_by(distance.asc())
            .limit(top_k)
        )

        rows = (await self.session.execute(stmt)).all()
        return [RagRetrievedChunk(chunk=row[0], distance=float(row[1])) for row in rows]

    async def answer(
        self,
        manifest_sha256: str,
        question: str,
        *,
        top_k: int = 8,
        run_id: UUID | None = None,
        ledger: LedgerService | None = None,
    ) -> tuple[str, list[RagRetrievedChunk]]:
        entries = await self.manifests.get_entries(manifest_sha256)
        artifact_to_path: dict[str, str] = {}
        for e in entries:
            artifact_to_path.setdefault(e.artifact_sha256, e.path)

        if ledger and run_id:
            await ledger.log_retrieval_query(
                run_id=run_id,
                kb_id=manifest_sha256,
                query=question,
                profile="rag_chunks",
            )

        retrieved = await self.retrieve(manifest_sha256, question, top_k=top_k)

        if ledger and run_id:
            await ledger.log_retrieval_result(
                run_id=run_id,
                kb_id=manifest_sha256,
                results=[
                    {
                        "chunk_id": str(r.chunk.id),
                        "artifact_sha256": r.chunk.artifact_sha256,
                        "path": artifact_to_path.get(r.chunk.artifact_sha256),
                        "distance": r.distance,
                    }
                    for r in retrieved
                ],
            )

        if not retrieved:
            return (
                "No indexed content found for this notebook. Run indexing first.",
                [],
            )

        sources_text = "\n\n".join(
            f"[{i}] {artifact_to_path.get(r.chunk.artifact_sha256) or r.chunk.artifact_sha256}\n{r.chunk.content}"
            for i, r in enumerate(retrieved, start=1)
        )

        system_prompt = (
            "You are a commercial analysis assistant.\n"
            "Use ONLY the provided sources. If the sources do not support an answer, say so.\n"
            "Cite sources with bracketed numbers like [1], [2].\n"
            "End with a short 'Confidence' line (High/Medium/Low) and 'Next steps'."
        )

        user_prompt = f"Question:\n{question}\n\nSources:\n{sources_text}\n\nAnswer:"

        client = self._get_openai()
        model = settings.chat_model

        start = perf_counter()
        if ledger and run_id:
            await ledger.log_llm_request(
                run_id=run_id,
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )

        resp = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )

        answer = resp.choices[0].message.content or ""

        if ledger and run_id:
            await ledger.log_llm_response(
                run_id=run_id,
                model=model,
                response={"answer": answer},
                duration_ms=int((perf_counter() - start) * 1000),
            )

        return answer, retrieved
