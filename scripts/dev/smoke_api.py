#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import time
from typing import Any

import httpx

from intelli.services.usage.pricing import PRICE_TABLE_VERSION, format_cost_usd


def _require(value: Any, msg: str) -> Any:
    if value is None:
        raise RuntimeError(msg)
    return value


def _print_ok(msg: str) -> None:
    print(f"OK: {msg}")


def _print_warn(msg: str) -> None:
    print(f"WARN: {msg}")


def _summarize_token_usage(run_payload: dict[str, Any]) -> dict[str, Any]:
    token_usage = run_payload.get("token_usage") or {}
    totals = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_micros": 0,
        "cost_by_model": [],
    }

    for model, usage in token_usage.items():
        if not isinstance(usage, dict):
            continue
        input_tokens = int(usage.get("input_tokens", usage.get("input", 0)) or 0)
        output_tokens = int(usage.get("output_tokens", usage.get("output", 0)) or 0)
        cost_micros = int(usage.get("cost_micros", 0) or 0)
        totals["input_tokens"] += input_tokens
        totals["output_tokens"] += output_tokens
        totals["cost_micros"] += cost_micros
        totals["cost_by_model"].append(
            {
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_micros": cost_micros,
            }
        )

    totals["cost_by_model"].sort(key=lambda item: (-item["cost_micros"], item["model"]))
    return totals


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
        "--usage-output",
        default=None,
        help="Optional path to write usage summary JSON",
    )
    parser.add_argument(
        "--require-rag",
        action="store_true",
        help="Fail if OPENAI_API_KEY missing or if RAG index/ask fails",
    )
    args = parser.parse_args()

    base_url: str = args.base_url.rstrip("/")
    require_rag: bool = args.require_rag
    usage_output: str | None = args.usage_output

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
        if usage_output:
            with open(usage_output, "w", encoding="utf-8") as f:
                json.dump({"price_table_version": PRICE_TABLE_VERSION, "runs": [], "totals": {}}, f)
        return 0

    try:
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
    except Exception as exc:
        if require_rag:
            raise
        _print_warn(f"optional RAG ask failed; skipping ({exc})")
        return 0

    _print_ok(f"rag ask (sources={len(sources)})")

    run_resp = client.get(f"/api/v1/runs/{ask_result['run_id']}", headers=headers)
    run_resp.raise_for_status()
    run_payload = run_resp.json()
    usage_summary = _summarize_token_usage(run_payload)
    summary = {
        "price_table_version": PRICE_TABLE_VERSION,
        "runs": [
            {
                "run_id": ask_result["run_id"],
                "session_id": run_payload.get("session_id"),
                "model": ask_result.get("model"),
                **usage_summary,
            }
        ],
        "totals": usage_summary,
    }

    print("USAGE SUMMARY:")
    print(f"  price table: {PRICE_TABLE_VERSION}")
    print(f"  run: {ask_result['run_id']}")
    print(f"  input tokens: {usage_summary['input_tokens']:,}")
    print(f"  output tokens: {usage_summary['output_tokens']:,}")
    print(f"  total cost: {format_cost_usd(usage_summary['cost_micros'])}")
    for item in usage_summary["cost_by_model"]:
        print(
            "  model"
            f" {item['model']}: {item['input_tokens']:,} in · {item['output_tokens']:,} out ·"
            f" {format_cost_usd(item['cost_micros'])}"
        )

    if usage_output:
        with open(usage_output, "w", encoding="utf-8") as f:
            json.dump(summary, f)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
