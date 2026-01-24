#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import time
from typing import Any

import httpx


def _require(value: Any, msg: str) -> Any:
    if value is None:
        raise RuntimeError(msg)
    return value


def _print_ok(msg: str) -> None:
    print(f"OK: {msg}")


def _print_warn(msg: str) -> None:
    print(f"WARN: {msg}")


def _load_dotenv_value(key: str, dotenv_path: str = ".env") -> str | None:
    try:
        with open(dotenv_path, encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() != key:
                    continue
                value = v.strip()
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]
                return value
    except FileNotFoundError:
        return None
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Backend smoke test (auth + substrate + optional RAG).")
    default_port = os.environ.get("INTELLI_API_PORT", "8000").strip() or "8000"
    parser.add_argument("--base-url", default=f"http://localhost:{default_port}", help="Backend base URL")
    parser.add_argument(
        "--require-rag",
        action="store_true",
        help="Fail if OPENAI_API_KEY missing or if RAG index/ask fails",
    )
    args = parser.parse_args()

    base_url: str = args.base_url.rstrip("/")
    require_rag: bool = args.require_rag

    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not openai_key:
        openai_key = (_load_dotenv_value("OPENAI_API_KEY") or "").strip()
    if require_rag and not openai_key:
        raise RuntimeError("OPENAI_API_KEY is required for --require-rag")

    client = httpx.Client(base_url=base_url, timeout=60.0)

    # Health
    r = client.get("/health/ready")
    r.raise_for_status()
    _print_ok("/health/ready")

    # Dev bootstrap login (requires DEBUG=true)
    r = client.post("/api/v1/auth/dev-bootstrap", json={})
    if r.status_code == 404:
        raise RuntimeError("dev-bootstrap disabled (set DEBUG=true on backend)")
    r.raise_for_status()
    login = r.json()
    token = _require(login.get("access_token"), "Missing access_token from dev-bootstrap")
    _print_ok("/api/v1/auth/dev-bootstrap")

    headers = {"Authorization": f"Bearer {token}"}

    # Create pointer (notebook)
    notebook_name = f"smoke-{int(time.time())}"
    r = client.post(
        "/api/v1/pointers",
        headers=headers,
        json={
            "namespace": "notebooks",
            "name": notebook_name,
            "pointer_type": "bundle",
            "description": "Smoke test notebook",
            "metadata": {"source": "smoke"},
        },
    )
    r.raise_for_status()
    pointer = r.json()
    pointer_id = _require(pointer.get("id"), "Missing pointer.id")
    _print_ok(f"create pointer notebooks/{notebook_name}")

    # Upload a tiny text artifact
    files = {"file": ("hello.txt", b"Hello world.\nThis is a smoke test document.\n", "text/plain")}
    r = client.post("/api/v1/artifacts", headers=headers, files=files)
    r.raise_for_status()
    upload = r.json()
    artifact_sha = _require(upload.get("sha256"), "Missing artifact sha256")
    _print_ok("upload artifact")

    # Create manifest with one entry
    r = client.post(
        "/api/v1/manifests",
        headers=headers,
        json={
            "entries": [{"path": "hello.txt", "artifact_sha256": artifact_sha, "metadata": {"source": "smoke"}}],
            "message": "Smoke manifest",
            "metadata": {"source": "smoke"},
        },
    )
    r.raise_for_status()
    manifest = r.json()
    manifest_sha = _require(manifest.get("sha256"), "Missing manifest sha256")
    _print_ok("create manifest")

    # Advance pointer
    r = client.put(
        f"/api/v1/pointers/{pointer_id}/advance",
        headers=headers,
        json={"manifest_sha256": manifest_sha, "expected_sha256": None, "reason": "smoke"},
    )
    r.raise_for_status()
    advance = r.json()
    if not advance.get("success", False):
        raise RuntimeError(f"Pointer advance failed: {advance}")
    _print_ok("advance pointer")

    if not openai_key:
        _print_warn("OPENAI_API_KEY not set; skipping RAG index/ask smoke steps")
        return 0

    # RAG index
    r = client.post(
        "/api/v1/rag/index",
        headers=headers,
        json={"pointer_id": pointer_id},
    )
    r.raise_for_status()
    index_result = r.json()
    _print_ok(f"rag index (chunks_created={index_result.get('chunks_created')})")

    # RAG ask
    r = client.post(
        "/api/v1/rag/ask",
        headers=headers,
        json={"pointer_id": pointer_id, "question": "What is this document?", "top_k": 5},
    )
    r.raise_for_status()
    ask_result = r.json()
    answer = (ask_result.get("answer") or "").strip()
    sources = ask_result.get("sources") or []

    if require_rag:
        if not answer:
            raise RuntimeError("RAG ask returned empty answer")
        if not sources:
            raise RuntimeError("RAG ask returned no sources")

    _print_ok(f"rag ask (sources={len(sources)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
