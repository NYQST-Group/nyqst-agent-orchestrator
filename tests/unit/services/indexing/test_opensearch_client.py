"""Unit tests for OpenSearchClient."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from intelli.services.indexing.opensearch_client import (
    OpenSearchClient,
    OpenSearchConfig,
    OpenSearchError,
)

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient."""
    client = MagicMock(spec=httpx.AsyncClient)
    client.get = AsyncMock()
    client.head = AsyncMock()
    client.put = AsyncMock()
    client.post = AsyncMock()
    client.aclose = AsyncMock()
    return client


@pytest.fixture
def opensearch_client(mock_httpx_client, monkeypatch):
    """Create OpenSearchClient with mocked httpx client."""
    config = OpenSearchConfig(
        base_url="http://localhost:9200",
        username="admin",
        password="admin",
    )
    client = OpenSearchClient(config)
    # Replace the internal httpx client with our mock
    client._client = mock_httpx_client
    return client


class TestPing:
    async def test_ping_success(self, opensearch_client, mock_httpx_client):
        response = MagicMock()
        response.status_code = 200
        mock_httpx_client.get.return_value = response

        result = await opensearch_client.ping()

        assert result is True
        mock_httpx_client.get.assert_called_once_with("/")

    async def test_ping_failure_returns_false(self, opensearch_client, mock_httpx_client):
        mock_httpx_client.get.side_effect = Exception("Connection error")

        result = await opensearch_client.ping()

        assert result is False


class TestIndexExists:
    async def test_index_exists_true(self, opensearch_client, mock_httpx_client):
        response = MagicMock()
        response.status_code = 200
        mock_httpx_client.head.return_value = response

        result = await opensearch_client.index_exists("test-index")

        assert result is True
        mock_httpx_client.head.assert_called_once_with("/test-index")

    async def test_index_exists_false(self, opensearch_client, mock_httpx_client):
        response = MagicMock()
        response.status_code = 404
        mock_httpx_client.head.return_value = response

        result = await opensearch_client.index_exists("test-index")

        assert result is False

    async def test_index_exists_unexpected_status_raises(
        self, opensearch_client, mock_httpx_client
    ):
        response = MagicMock()
        response.status_code = 500
        response.text = "Internal Server Error"
        mock_httpx_client.head.return_value = response

        with pytest.raises(OpenSearchError) as exc_info:
            await opensearch_client.index_exists("test-index")

        assert "Unexpected response checking index exists" in str(exc_info.value)
        assert "500" in str(exc_info.value)


class TestCreateIndex:
    async def test_create_index_success(self, opensearch_client, mock_httpx_client):
        response = MagicMock()
        response.status_code = 200
        mock_httpx_client.put.return_value = response

        body = {"settings": {"index": {"knn": True}}}
        await opensearch_client.create_index("test-index", body=body)

        mock_httpx_client.put.assert_called_once_with("/test-index", json=body)

    async def test_create_index_failure_raises(self, opensearch_client, mock_httpx_client):
        response = MagicMock()
        response.status_code = 400
        response.text = "Bad Request"
        mock_httpx_client.put.return_value = response

        with pytest.raises(OpenSearchError) as exc_info:
            await opensearch_client.create_index("test-index", body={})

        assert "Create index failed" in str(exc_info.value)
        assert "400" in str(exc_info.value)


class TestDeleteByQuery:
    async def test_delete_by_query_success(self, opensearch_client, mock_httpx_client):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"deleted": 5}
        mock_httpx_client.post.return_value = response

        query = {"term": {"field": "value"}}
        result = await opensearch_client.delete_by_query("test-index", query=query, refresh=True)

        assert result == {"deleted": 5}
        mock_httpx_client.post.assert_called_once_with(
            "/test-index/_delete_by_query",
            params={"refresh": "true"},
            json={"query": query},
        )


class TestSearch:
    async def test_search_success(self, opensearch_client, mock_httpx_client):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "hits": {
                "total": {"value": 1},
                "hits": [{"_id": "1", "_source": {"field": "value"}}],
            }
        }
        mock_httpx_client.post.return_value = response

        body = {"query": {"match_all": {}}}
        result = await opensearch_client.search("test-index", body=body)

        assert result["hits"]["total"]["value"] == 1
        mock_httpx_client.post.assert_called_once_with("/test-index/_search", json=body)


class TestBulk:
    async def test_bulk_success(self, opensearch_client, mock_httpx_client):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"errors": False, "items": []}
        mock_httpx_client.post.return_value = response

        body_lines = [
            {"index": {"_index": "test", "_id": "1"}},
            {"field": "value"},
        ]
        result = await opensearch_client.bulk(body_lines=body_lines)

        assert result["errors"] is False
        mock_httpx_client.post.assert_called_once()
        call_kwargs = mock_httpx_client.post.call_args.kwargs
        assert call_kwargs["headers"]["Content-Type"] == "application/x-ndjson"

    async def test_bulk_with_errors_raises(self, opensearch_client, mock_httpx_client):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "errors": True,
            "items": [{"index": {"error": "some error"}}],
        }
        mock_httpx_client.post.return_value = response

        with pytest.raises(OpenSearchError) as exc_info:
            await opensearch_client.bulk(body_lines=[])

        assert "Bulk contained errors" in str(exc_info.value)


class TestClose:
    async def test_aclose_closes_client(self, opensearch_client, mock_httpx_client):
        await opensearch_client.aclose()

        mock_httpx_client.aclose.assert_called_once()
