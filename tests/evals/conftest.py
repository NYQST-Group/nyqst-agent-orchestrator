"""Conftest for eval tests — registers the 'eval' marker and skips by default."""

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "eval: marks tests that hit the real OpenAI API (deselect with '-m \"not eval\"')",
    )


def pytest_collection_modifyitems(config, items):
    """Skip eval tests unless explicitly requested with -m eval."""
    # If the user explicitly passed -m eval, don't skip
    markexpr = config.getoption("-m", default="")
    if "eval" in markexpr:
        return

    skip_eval = pytest.mark.skip(reason="Eval tests require -m eval (hits real OpenAI API)")
    for item in items:
        if "eval" in item.keywords:
            item.add_marker(skip_eval)
