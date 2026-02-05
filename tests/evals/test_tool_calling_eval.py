"""Live LLM evaluation tests for tool calling behaviour.

These tests hit the REAL OpenAI API. They are SKIPPED by default.
Run them explicitly with:

    pytest tests/evals/ -m eval -v --tb=short

They verify that the configured model (CHAT_MODEL in .env) reliably:
1. Calls the correct tool for each query type
2. Passes the right argument keys
3. Does NOT call tools when inappropriate (greetings)
4. Produces output directly instead of asking for format preferences

Each test case is defined in test_cases.jsonl alongside this file.
Results are written to tests/evals/results/ for inspection.

Uses seed + low temperature for reproducibility across runs.
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from intelli.agents.graphs.research_assistant import SYSTEM_PROMPT
from intelli.agents.tools.research_tools import build_research_tools
from intelli.config import settings

# Mark ALL tests in this file — skipped unless `pytest -m eval`
pytestmark = pytest.mark.eval  # noqa: E501  (not the builtin eval function)

EVALS_DIR = Path(__file__).parent
CASES_PATH = EVALS_DIR / "test_cases.jsonl"
RESULTS_DIR = EVALS_DIR / "results"

# Manifest used in system prompt (doesn't need to be real —
# we're testing the LLM's tool-calling decisions, not RAG retrieval)
EVAL_MANIFEST = "evaluation_" + "0" * 54


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def llm():
    """Create a real ChatOpenAI with seed=42, temperature=0."""
    api_key = settings.openai_api_key
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")

    kwargs = {
        "model": settings.chat_model,
        "api_key": api_key,
        "temperature": 0,
        "seed": 42,
    }
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url

    return ChatOpenAI(**kwargs)


@pytest.fixture(scope="session")
def tool_schemas():
    """Get the LangChain tool objects for bind_tools."""
    from unittest.mock import AsyncMock

    return build_research_tools(AsyncMock())


@pytest.fixture(scope="session")
def bound_llm(llm, tool_schemas):
    """LLM with tools bound."""
    return llm.bind_tools(tool_schemas)


@pytest.fixture(scope="session")
def system_message():
    """Formatted system message with the evaluation manifest."""
    return SystemMessage(content=SYSTEM_PROMPT.format(manifest_sha256=EVAL_MANIFEST))


@pytest.fixture(scope="session", autouse=True)
def results_dir():
    """Ensure results directory exists."""
    RESULTS_DIR.mkdir(exist_ok=True)
    return RESULTS_DIR


# ---------------------------------------------------------------------------
# Core runner
# ---------------------------------------------------------------------------


def _run_single(bound_llm, system_message, user_input: str) -> dict:
    """Send a single message and capture tool call decisions."""
    messages = [system_message, HumanMessage(content=user_input)]

    start = time.monotonic()
    response: AIMessage = bound_llm.invoke(messages)
    elapsed_ms = int((time.monotonic() - start) * 1000)

    tool_calls = response.tool_calls or []

    return {
        "content": response.content or "",
        "tool_calls": [
            {"name": tc["name"], "args": tc["args"], "id": tc["id"]} for tc in tool_calls
        ],
        "has_tool_call": len(tool_calls) > 0,
        "first_tool": tool_calls[0]["name"] if tool_calls else None,
        "first_args": tool_calls[0]["args"] if tool_calls else None,
        "elapsed_ms": elapsed_ms,
    }


# ---------------------------------------------------------------------------
# Load cases for parametrize
# ---------------------------------------------------------------------------


def _load_cases():
    if not CASES_PATH.exists():
        return []
    cases = []
    with open(CASES_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases


# ---------------------------------------------------------------------------
# Parametrized test
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case", _load_cases(), ids=lambda c: c["id"])
def test_tool_calling(case, bound_llm, system_message, results_dir):
    """Test a single case against the live LLM.

    Asserts:
    - Tool called / not called as expected
    - Correct tool name
    - Required argument keys present
    - No anti-patterns (asking format, listing capabilities)
    """
    result = _run_single(bound_llm, system_message, case["input"])

    record = {
        "case_id": case["id"],
        "input": case["input"],
        "description": case.get("description", ""),
        "expected_tool": case.get("expected_tool"),
        "expect_tool_call": case["expect_tool_call"],
        "actual_tool": result["first_tool"],
        "actual_args": result["first_args"],
        "has_tool_call": result["has_tool_call"],
        "content_preview": result["content"][:200],
        "elapsed_ms": result["elapsed_ms"],
        "passed": True,
        "failure_reason": None,
    }

    try:
        # 1. Tool call presence
        if case["expect_tool_call"]:
            assert result["has_tool_call"], (
                f"Expected tool call but got direct response: {result['content'][:100]}"
            )
        else:
            assert not result["has_tool_call"], (
                f"Expected NO tool call but got: {result['first_tool']}({result['first_args']})"
            )

        # 2. Correct tool name
        if case.get("expected_tool") and result["has_tool_call"]:
            assert result["first_tool"] == case["expected_tool"], (
                f"Expected '{case['expected_tool']}' but got '{result['first_tool']}'"
            )

        # 3. Required argument keys
        if case.get("expected_args_contains") and result["first_args"]:
            for key in case["expected_args_contains"]:
                assert key in result["first_args"], (
                    f"Missing argument '{key}' from {result['first_args']}"
                )

        # 4. Anti-patterns
        if case["expect_tool_call"]:
            content_lower = result["content"].lower()
            assert "which format" not in content_lower, (
                "Agent asked 'which format' instead of acting"
            )

    except AssertionError as e:
        record["passed"] = False
        record["failure_reason"] = str(e)
        raise
    finally:
        result_path = results_dir / f"{case['id']}.json"
        with open(result_path, "w") as f:
            json.dump(record, f, indent=2, default=str)


# ---------------------------------------------------------------------------
# Summary report
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session", autouse=True)
def write_summary(results_dir, request):
    """Write summary.json after all tests complete."""
    yield

    results = []
    for p in sorted(results_dir.glob("*.json")):
        if p.name == "summary.json":
            continue
        with open(p) as f:
            results.append(json.loads(f.read()))

    if not results:
        return

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    avg_latency = sum(r["elapsed_ms"] for r in results) / total

    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "model": settings.chat_model,
        "total_cases": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": f"{passed / total:.0%}",
        "avg_latency_ms": int(avg_latency),
        "failures": [
            {"id": r["case_id"], "reason": r["failure_reason"]} for r in results if not r["passed"]
        ],
    }

    with open(results_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"TOOL CALLING RESULTS: {passed}/{total} ({summary['pass_rate']})")
    print(f"Model: {settings.chat_model} | Avg latency: {int(avg_latency)}ms")
    if summary["failures"]:
        print("Failures:")
        for fail in summary["failures"]:
            print(f"  - {fail['id']}: {fail['reason'][:80]}")
    print(f"{'=' * 60}\n")
