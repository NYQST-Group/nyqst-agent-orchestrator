"""Pytest fixtures for agent tests.

This module provides fixtures that are automatically used by all tests
in the agents module, including mocking the LLM initialization.
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_chat_openai():
    """Mock ChatOpenAI to avoid requiring OPENAI_API_KEY in tests.

    This fixture is automatically applied to all tests in the agents module.
    It prevents the ResearchAssistantGraph.__init__ from attempting to create
    a real ChatOpenAI client that requires API credentials.

    Individual tests can override the LLM behavior by patching graph._get_llm()
    or graph._llm directly.
    """
    with patch("intelli.agents.graphs.research_assistant.ChatOpenAI") as mock_openai:
        # Create a mock instance that supports common LLM operations
        mock_instance = MagicMock()
        mock_instance.bind_tools = MagicMock(return_value=mock_instance)
        mock_instance.ainvoke = MagicMock()
        mock_instance.invoke = MagicMock()

        # Return the mock instance when ChatOpenAI is instantiated
        mock_openai.return_value = mock_instance

        yield mock_openai
