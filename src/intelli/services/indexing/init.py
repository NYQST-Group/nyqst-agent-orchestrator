"""Index backend initialization at app startup."""

from __future__ import annotations

from intelli.config import settings
from intelli.services.indexing.opensearch_chunks import OpenSearchChunkIndex
from intelli.services.indexing.opensearch_client import OpenSearchClient, OpenSearchConfig


async def init_index_backend() -> None:
    if settings.index_backend != "opensearch":
        return

    client = OpenSearchClient(
        OpenSearchConfig(
            base_url=settings.opensearch_url,
            username=settings.opensearch_username,
            password=settings.opensearch_password,
            verify_certs=settings.opensearch_verify_certs,
        )
    )
    try:
        idx = OpenSearchChunkIndex(client)
        await idx.ensure_index()
    finally:
        await client.aclose()
