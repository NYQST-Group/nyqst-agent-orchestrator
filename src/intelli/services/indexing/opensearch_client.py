"""Minimal async OpenSearch HTTP client.

We use HTTP calls (via httpx) to keep the integration lightweight and explicit.
The goal is to make the index backend swappable without coupling the codebase to a
specific SDK.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class OpenSearchConfig:
    base_url: str
    username: str | None = None
    password: str | None = None
    verify_certs: bool = False


class OpenSearchError(RuntimeError):
    pass


class OpenSearchClient:
    def __init__(self, cfg: OpenSearchConfig):
        self.cfg = cfg
        self._client = httpx.AsyncClient(
            base_url=self.cfg.base_url.rstrip("/"),
            timeout=30.0,
            verify=self.cfg.verify_certs,
            auth=(self.cfg.username, self.cfg.password) if self.cfg.username and self.cfg.password else None,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def ping(self) -> bool:
        try:
            resp = await self._client.get("/")
            return resp.status_code == 200
        except Exception:
            return False

    async def index_exists(self, index: str) -> bool:
        resp = await self._client.head(f"/{index}")
        if resp.status_code == 200:
            return True
        if resp.status_code == 404:
            return False
        raise OpenSearchError(f"Unexpected response checking index exists: {resp.status_code} {resp.text}")

    async def create_index(self, index: str, *, body: dict) -> None:
        resp = await self._client.put(f"/{index}", json=body)
        if resp.status_code not in (200, 201):
            raise OpenSearchError(f"Create index failed: {resp.status_code} {resp.text}")

    async def delete_by_query(self, index: str, *, query: dict, refresh: bool = False) -> dict:
        params = {"refresh": "true"} if refresh else None
        resp = await self._client.post(f"/{index}/_delete_by_query", params=params, json={"query": query})
        if resp.status_code != 200:
            raise OpenSearchError(f"Delete by query failed: {resp.status_code} {resp.text}")
        return resp.json()

    async def search(self, index: str, *, body: dict) -> dict:
        resp = await self._client.post(f"/{index}/_search", json=body)
        if resp.status_code != 200:
            raise OpenSearchError(f"Search failed: {resp.status_code} {resp.text}")
        return resp.json()

    async def bulk(self, *, body_lines: list[dict]) -> dict:
        ndjson = "\n".join(json.dumps(line, separators=(",", ":")) for line in body_lines) + "\n"
        resp = await self._client.post(
            "/_bulk",
            content=ndjson,
            headers={"Content-Type": "application/x-ndjson"},
        )
        if resp.status_code != 200:
            raise OpenSearchError(f"Bulk failed: {resp.status_code} {resp.text}")
        payload = resp.json()
        if payload.get("errors") is True:
            raise OpenSearchError(f"Bulk contained errors: {payload}")
        return payload

