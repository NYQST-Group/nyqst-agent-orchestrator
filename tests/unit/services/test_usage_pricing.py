"""Unit tests for usage pricing helpers."""

import pytest

from intelli.services.usage.pricing import estimate_cost_micros, format_cost_usd

pytestmark = pytest.mark.unit


class TestEstimateCostMicros:
    def test_gpt_5_nano(self):
        cost = estimate_cost_micros("gpt-5-nano", input_tokens=1000, output_tokens=500)
        assert cost == 250

    def test_embedding_model(self):
        cost = estimate_cost_micros("text-embedding-3-small", input_tokens=1000)
        assert cost == 20

    def test_unknown_model_returns_zero(self):
        assert estimate_cost_micros("unknown-model", input_tokens=1000) == 0

    def test_negative_tokens_clamped_to_zero(self):
        assert estimate_cost_micros("gpt-5-nano", input_tokens=-100, output_tokens=-50) == 0


class TestFormatCostUsd:
    def test_zero(self):
        assert format_cost_usd(0) == "$0.00"

    def test_negative_treated_as_zero(self):
        assert format_cost_usd(-100) == "$0.00"

    def test_above_one_dollar(self):
        assert format_cost_usd(1_500_000) == "$1.50"

    def test_sub_dollar_above_cent(self):
        assert format_cost_usd(15_000) == "$0.0150"

    def test_sub_cent(self):
        assert format_cost_usd(456) == "$0.000456"

    def test_one_micro(self):
        assert format_cost_usd(1) == "$0.000001"

    def test_sub_cent_no_bare_dollar(self):
        """Regression: rstrip must not collapse to bare '$0'."""
        # Any non-zero input must produce a string with a decimal point
        for micros in [1, 2, 5, 10, 100, 456, 999]:
            result = format_cost_usd(micros)
            assert "." in result, f"format_cost_usd({micros}) = {result!r} has no decimal"
            assert result != "$0", f"format_cost_usd({micros}) produced bare '$0'"
            assert len(result) > 2, f"format_cost_usd({micros}) = {result!r} too short"
