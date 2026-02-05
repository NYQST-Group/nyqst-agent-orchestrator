"""Unit tests for OpenSearchChunkIndex."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from intelli.services.indexing.opensearch_chunks import (
    IndexedChunk,
    OpenSearchChunkIndex,
    chunk_uuid,
)

# Most tests are async, but TestChunkUuid tests are synchronous
pytestmark = [pytest.mark.unit]


class TestChunkUuid:
    def test_chunk_uuid_deterministic(self):
        """Same inputs produce same UUID."""
        uuid1 = chunk_uuid(
            artifact_sha256="abc123",
            embedding_model="text-embedding-3-small",
            chunk_index=0,
        )
        uuid2 = chunk_uuid(
            artifact_sha256="abc123",
            embedding_model="text-embedding-3-small",
            chunk_index=0,
        )
        assert uuid1 == uuid2
        assert isinstance(uuid1, UUID)

    def test_chunk_uuid_differs_for_different_inputs(self):
        """Different inputs produce different UUIDs."""
        uuid1 = chunk_uuid(
            artifact_sha256="abc123",
            embedding_model="text-embedding-3-small",
            chunk_index=0,
        )
        uuid2 = chunk_uuid(
            artifact_sha256="abc123",
            embedding_model="text-embedding-3-small",
            chunk_index=1,
        )
        uuid3 = chunk_uuid(
            artifact_sha256="def456",
            embedding_model="text-embedding-3-small",
            chunk_index=0,
        )
        assert uuid1 != uuid2
        assert uuid1 != uuid3
        assert uuid2 != uuid3


@pytest.fixture
def mock_opensearch_client():
    """Mock OpenSearchClient."""
    client = MagicMock()
    client.index_exists = AsyncMock(return_value=True)
    client.create_index = AsyncMock()
    client.delete_by_query = AsyncMock()
    client.bulk = AsyncMock()
    client.search = AsyncMock()
    return client


@pytest.fixture
def chunk_index(mock_opensearch_client):
    """Create OpenSearchChunkIndex with mocked client."""
    return OpenSearchChunkIndex(mock_opensearch_client, index_name="test-chunks")


@pytest.mark.asyncio
class TestEnsureIndex:
    async def test_ensure_index_creates_when_missing(self, chunk_index, mock_opensearch_client):
        mock_opensearch_client.index_exists.return_value = False

        await chunk_index.ensure_index()

        mock_opensearch_client.index_exists.assert_called_once_with("test-chunks")
        mock_opensearch_client.create_index.assert_called_once()
        # Verify the body has the expected structure
        call_args = mock_opensearch_client.create_index.call_args
        assert call_args[0][0] == "test-chunks"
        body = call_args[1]["body"]
        assert body["settings"]["index"]["knn"] is True
        assert "embedding" in body["mappings"]["properties"]
        assert body["mappings"]["properties"]["embedding"]["type"] == "knn_vector"

    async def test_ensure_index_skips_when_exists(self, chunk_index, mock_opensearch_client):
        mock_opensearch_client.index_exists.return_value = True

        await chunk_index.ensure_index()

        mock_opensearch_client.index_exists.assert_called_once_with("test-chunks")
        mock_opensearch_client.create_index.assert_not_called()


@pytest.mark.asyncio
class TestDeleteArtifact:
    async def test_delete_artifact_sends_delete_by_query(self, chunk_index, mock_opensearch_client):
        await chunk_index.delete_artifact(
            artifact_sha256="abc123",
            embedding_model="text-embedding-3-small",
        )

        mock_opensearch_client.delete_by_query.assert_called_once()
        call_args = mock_opensearch_client.delete_by_query.call_args
        assert call_args[0][0] == "test-chunks"
        query = call_args[1]["query"]
        assert query["bool"]["filter"][0] == {"term": {"artifact_sha256": "abc123"}}
        assert query["bool"]["filter"][1] == {"term": {"embedding_model": "text-embedding-3-small"}}
        assert call_args[1]["refresh"] is True


@pytest.mark.asyncio
class TestUpsertChunks:
    async def test_upsert_chunks_replaces_existing(self, chunk_index, mock_opensearch_client):
        chunks = ["chunk 1", "chunk 2"]
        embeddings = [[0.1, 0.2], [0.3, 0.4]]

        await chunk_index.upsert_chunks(
            artifact_sha256="abc123",
            embedding_model="text-embedding-3-small",
            path_hint="doc.pdf",
            chunks=chunks,
            embeddings=embeddings,
        )

        # Should delete existing chunks first
        mock_opensearch_client.delete_by_query.assert_called_once()

        # Should bulk index new chunks
        mock_opensearch_client.bulk.assert_called_once()
        call_args = mock_opensearch_client.bulk.call_args
        body_lines = call_args[1]["body_lines"]

        # Should have 2 chunks × 2 lines per chunk (index operation + document)
        assert len(body_lines) == 4
        assert body_lines[0] == {
            "index": {"_index": "test-chunks", "_id": body_lines[0]["index"]["_id"]}
        }
        assert body_lines[1]["content"] == "chunk 1"
        assert body_lines[1]["embedding"] == [0.1, 0.2]
        assert body_lines[1]["path_hint"] == "doc.pdf"
        assert body_lines[3]["content"] == "chunk 2"

    async def test_upsert_chunks_empty_is_noop(self, chunk_index, mock_opensearch_client):
        await chunk_index.upsert_chunks(
            artifact_sha256="abc123",
            embedding_model="text-embedding-3-small",
            path_hint="doc.pdf",
            chunks=[],
            embeddings=[],
        )

        # Should still delete existing chunks
        mock_opensearch_client.delete_by_query.assert_called_once()
        # But should not bulk index anything
        mock_opensearch_client.bulk.assert_not_called()


@pytest.mark.asyncio
class TestSearchHybrid:
    async def test_search_hybrid_combines_bm25_and_knn(self, chunk_index, mock_opensearch_client):
        # Use valid UUIDs for _id fields
        from uuid import uuid4

        chunk_id_1 = str(uuid4())
        chunk_id_2 = str(uuid4())

        # Mock BM25 results
        bm25_response = {
            "hits": {
                "hits": [
                    {
                        "_id": chunk_id_1,
                        "_source": {
                            "artifact_sha256": "abc123",
                            "chunk_index": 0,
                            "content": "test content",
                            "path_hint": "doc.pdf",
                        },
                    }
                ]
            }
        }

        # Mock kNN results
        knn_response = {
            "hits": {
                "hits": [
                    {
                        "_id": chunk_id_2,
                        "_source": {
                            "artifact_sha256": "def456",
                            "chunk_index": 1,
                            "content": "other content",
                            "path_hint": "other.pdf",
                        },
                    }
                ]
            }
        }

        # First call returns BM25, second returns kNN
        mock_opensearch_client.search.side_effect = [bm25_response, knn_response]

        results = await chunk_index.search_hybrid(
            query_text="test query",
            query_embedding=[0.1, 0.2, 0.3],
            artifact_sha256s=["abc123", "def456"],
            embedding_model="text-embedding-3-small",
            top_k=8,
        )

        # Should call search twice (BM25 and kNN)
        assert mock_opensearch_client.search.call_count == 2

        # Should return combined results
        assert len(results) == 2
        assert all(isinstance(r, IndexedChunk) for r in results)
        assert results[0].content in ["test content", "other content"]
        assert results[1].content in ["test content", "other content"]

    async def test_search_hybrid_handles_empty_results(self, chunk_index, mock_opensearch_client):
        empty_response = {"hits": {"hits": []}}
        mock_opensearch_client.search.side_effect = [empty_response, empty_response]

        results = await chunk_index.search_hybrid(
            query_text="test query",
            query_embedding=[0.1, 0.2, 0.3],
            artifact_sha256s=["abc123"],
            embedding_model="text-embedding-3-small",
        )

        assert results == []
