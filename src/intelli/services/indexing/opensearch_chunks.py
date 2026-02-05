"""OpenSearch-backed chunk index (BM25 + vector).

Stores chunk documents:
- `content` for BM25
- `embedding` for kNN
- metadata for traceability back to immutable artifacts
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid5

from intelli.config import settings
from intelli.services.indexing.opensearch_client import OpenSearchClient

CHUNK_ID_NAMESPACE = UUID("c40b4f0c-1c6f-4e75-bd5d-4fd2c05c5e6e")


def chunk_uuid(*, artifact_sha256: str, embedding_model: str, chunk_index: int) -> UUID:
    return uuid5(CHUNK_ID_NAMESPACE, f"{artifact_sha256}:{embedding_model}:{chunk_index}")


@dataclass(frozen=True)
class IndexedChunk:
    chunk_id: UUID
    artifact_sha256: str
    chunk_index: int
    content: str
    score: float
    path_hint: str | None = None


class OpenSearchChunkIndex:
    def __init__(self, client: OpenSearchClient, *, index_name: str | None = None):
        self.client = client
        self.index_name = index_name or settings.opensearch_chunks_index

    async def ensure_index(self) -> None:
        if await self.client.index_exists(self.index_name):
            return

        # Minimal k-NN index definition. We keep this intentionally conservative so we
        # can evolve settings without breaking the contract.
        body = {
            "settings": {
                "index": {
                    "knn": True,
                }
            },
            "mappings": {
                "properties": {
                    "artifact_sha256": {"type": "keyword"},
                    "embedding_model": {"type": "keyword"},
                    "chunk_index": {"type": "integer"},
                    "path_hint": {"type": "keyword"},
                    "content": {"type": "text"},
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": settings.embedding_dimensions,
                        "method": {
                            "name": "hnsw",
                            "space_type": "cosinesimil",
                            "engine": "lucene",
                        },
                    },
                }
            },
        }
        await self.client.create_index(self.index_name, body=body)

    async def delete_artifact(self, *, artifact_sha256: str, embedding_model: str) -> None:
        await self.ensure_index()
        await self.client.delete_by_query(
            self.index_name,
            query={
                "bool": {
                    "filter": [
                        {"term": {"artifact_sha256": artifact_sha256}},
                        {"term": {"embedding_model": embedding_model}},
                    ]
                }
            },
            refresh=True,
        )

    async def upsert_chunks(
        self,
        *,
        artifact_sha256: str,
        embedding_model: str,
        path_hint: str | None,
        chunks: list[str],
        embeddings: list[list[float]],
    ) -> None:
        await self.ensure_index()

        # Replace all chunks for this artifact+model (keeps index consistent even if chunking changes).
        await self.delete_artifact(artifact_sha256=artifact_sha256, embedding_model=embedding_model)

        body_lines: list[dict] = []
        for idx, (content, emb) in enumerate(zip(chunks, embeddings, strict=True)):
            doc_id = str(
                chunk_uuid(
                    artifact_sha256=artifact_sha256,
                    embedding_model=embedding_model,
                    chunk_index=idx,
                )
            )
            body_lines.append({"index": {"_index": self.index_name, "_id": doc_id}})
            body_lines.append(
                {
                    "artifact_sha256": artifact_sha256,
                    "embedding_model": embedding_model,
                    "chunk_index": idx,
                    "path_hint": path_hint,
                    "content": content,
                    "embedding": emb,
                }
            )

        if not body_lines:
            return

        await self.client.bulk(body_lines=body_lines)

    async def search_hybrid(
        self,
        *,
        query_text: str,
        query_embedding: list[float],
        artifact_sha256s: list[str],
        embedding_model: str,
        top_k: int = 8,
        rrf_k: int = 60,
    ) -> list[IndexedChunk]:
        await self.ensure_index()

        # BM25
        bm25 = await self.client.search(
            self.index_name,
            body={
                "size": top_k,
                "_source": ["artifact_sha256", "chunk_index", "content", "path_hint"],
                "query": {
                    "bool": {
                        "filter": [
                            {"terms": {"artifact_sha256": artifact_sha256s}},
                            {"term": {"embedding_model": embedding_model}},
                        ],
                        "must": [{"match": {"content": {"query": query_text}}}],
                    }
                },
            },
        )

        # kNN
        knn = await self.client.search(
            self.index_name,
            body={
                "size": top_k,
                "_source": ["artifact_sha256", "chunk_index", "content", "path_hint"],
                "query": {
                    "bool": {
                        "filter": [
                            {"terms": {"artifact_sha256": artifact_sha256s}},
                            {"term": {"embedding_model": embedding_model}},
                        ],
                        "must": [
                            {
                                "knn": {
                                    "embedding": {
                                        "vector": query_embedding,
                                        "k": top_k,
                                    }
                                }
                            }
                        ],
                    }
                },
            },
        )

        def _hits(resp: dict) -> list[dict]:
            return (resp.get("hits") or {}).get("hits") or []

        # Reciprocal Rank Fusion (RRF)
        ranks: dict[str, float] = {}
        sources: dict[str, dict] = {}

        for result_set in (_hits(bm25), _hits(knn)):
            for rank, hit in enumerate(result_set, start=1):
                doc_id = str(hit.get("_id"))
                ranks[doc_id] = ranks.get(doc_id, 0.0) + 1.0 / float(rrf_k + rank)
                if doc_id not in sources:
                    sources[doc_id] = hit.get("_source") or {}

        ordered = sorted(ranks.items(), key=lambda kv: kv[1], reverse=True)[:top_k]

        out: list[IndexedChunk] = []
        for doc_id, score in ordered:
            src = sources.get(doc_id) or {}
            out.append(
                IndexedChunk(
                    chunk_id=UUID(doc_id),
                    artifact_sha256=str(src.get("artifact_sha256")),
                    chunk_index=int(src.get("chunk_index") or 0),
                    content=str(src.get("content") or ""),
                    score=float(score),
                    path_hint=(src.get("path_hint") or None),
                )
            )
        return out
