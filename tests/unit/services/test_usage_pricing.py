"""Unit tests for usage pricing helpers."""

import pytest

from intelli.services.usage.pricing import estimate_cost_micros, format_cost_usd

pytestmark = pytest.mark.unit


def test_estimate_cost_micros_for_gpt_5_nano():
    cost = estimate_cost_micros("gpt-5-nano", input_tokens=1000, output_tokens=500)
    assert cost == 250


def test_estimate_cost_micros_for_embedding_model():
    cost = estimate_cost_micros("text-embedding-3-small", input_tokens=1000)
    assert cost == 20


def test_format_cost_usd_handles_small_values():
    assert format_cost_usd(456) == "$0.000456"
    assert format_cost_usd(0) == "$0.00"
