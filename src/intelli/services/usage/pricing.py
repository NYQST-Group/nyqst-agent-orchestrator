"""Model pricing and deterministic cost estimation helpers."""

from __future__ import annotations

from dataclasses import dataclass

PRICE_TABLE_VERSION = "openai-2026-03-14"


@dataclass(frozen=True)
class ModelPricing:
    """Pricing in USD per 1M tokens."""

    input_cost_per_1m_tokens: float
    output_cost_per_1m_tokens: float
    cached_input_cost_per_1m_tokens: float | None = None
    effective_from: str = "2026-03-14"


# Pricing sourced from OpenAI public pricing pages on 2026-03-14.
MODEL_PRICING: dict[str, ModelPricing] = {
    "gpt-5-nano": ModelPricing(
        input_cost_per_1m_tokens=0.05,
        output_cost_per_1m_tokens=0.40,
    ),
    "text-embedding-3-small": ModelPricing(
        input_cost_per_1m_tokens=0.02,
        output_cost_per_1m_tokens=0.0,
    ),
}


def estimate_cost_micros(
    model: str,
    *,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cached_input_tokens: int = 0,
) -> int:
    """Estimate cost in micros of USD for a model usage record."""
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        return 0

    total_usd = (max(input_tokens, 0) / 1_000_000) * pricing.input_cost_per_1m_tokens + (
        max(output_tokens, 0) / 1_000_000
    ) * pricing.output_cost_per_1m_tokens

    if pricing.cached_input_cost_per_1m_tokens is not None and cached_input_tokens > 0:
        total_usd += (cached_input_tokens / 1_000_000) * pricing.cached_input_cost_per_1m_tokens

    return int(round(total_usd * 1_000_000))


def format_cost_usd(cost_micros: int) -> str:
    """Format micros of USD into a compact dollar string.

    Always returns a well-formed dollar string with at least two decimal places.
    """
    usd = max(cost_micros, 0) / 1_000_000
    if usd == 0:
        return "$0.00"
    if usd >= 1:
        return f"${usd:.2f}"
    if usd >= 0.01:
        return f"${usd:.4f}"
    formatted = f"${usd:.6f}".rstrip("0").rstrip(".")
    # Guard: if rstrip collapsed all decimals (e.g. sub-micro values that
    # round to $0.000000), fall back to $0.00 instead of bare "$0".
    if len(formatted) <= 2 or "." not in formatted:
        return "$0.00"
    return formatted
