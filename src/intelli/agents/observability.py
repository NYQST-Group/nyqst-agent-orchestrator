"""Observability integrations for agent execution.

Provides callback handlers for tracing agent execution with Langfuse.
"""

from intelli.config import settings


def get_langfuse_handler(session_id: str, user_id: str | None = None):
    """Get Langfuse callback handler for tracing.

    Args:
        session_id: Session ID for grouping traces
        user_id: Optional user ID for user-level analytics

    Returns:
        CallbackHandler instance if Langfuse is enabled, None otherwise

    Example:
        >>> handler = get_langfuse_handler(session_id="abc-123", user_id="user-456")
        >>> callbacks = [handler] if handler else []
        >>> graph.astream_events(state, config={"callbacks": callbacks})
    """
    if not settings.langfuse_enabled:
        return None

    try:
        from langfuse.callback import CallbackHandler

        return CallbackHandler(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
            session_id=session_id,
            user_id=user_id,
        )
    except ImportError:
        # Langfuse not installed (optional dependency)
        return None
