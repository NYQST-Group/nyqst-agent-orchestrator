# Observability

## Overview

Intelli includes optional integration with [Langfuse](https://langfuse.com) for tracing and monitoring agent execution. When enabled, all agent runs are automatically traced with detailed information about LLM calls, tool usage, and performance metrics.

## Features

- **Automatic tracing**: All agent chat sessions are traced without code changes
- **Session grouping**: Traces are grouped by session ID for conversation-level analytics
- **User attribution**: Optional user ID tracking for user-level analytics
- **Zero overhead when disabled**: No performance impact when observability is turned off
- **Graceful degradation**: Works without the langfuse package installed

## Quick Start

### Option 1: Local Langfuse (Docker)

1. Start Langfuse locally using the observability profile:

```bash
docker compose --profile observability up -d
```

2. Visit http://localhost:3000 and create an account

3. Create a new project and get your API keys

4. Add to your `.env`:

```bash
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=http://localhost:3000
```

5. Install the optional dependency:

```bash
pip install -e ".[observability]"
```

6. Restart the API server - traces will now appear in Langfuse

### Option 2: Langfuse Cloud

1. Sign up at [cloud.langfuse.com](https://cloud.langfuse.com)

2. Create a project and get your API keys

3. Add to your `.env`:

```bash
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

4. Install the optional dependency:

```bash
pip install -e ".[observability]"
```

5. Restart the API server

## What Gets Traced

When Langfuse is enabled, each agent chat session creates a trace containing:

- **Session metadata**: session_id, user_id, conversation_id
- **LLM calls**: Model, prompt, completion, tokens, latency
- **Tool calls**: Tool name, input, output, execution time
- **Errors**: Any exceptions or failures during execution
- **Performance metrics**: End-to-end latency, token usage

## Configuration

All configuration is via environment variables (defined in `src/intelli/config.py`):

| Variable | Default | Description |
|----------|---------|-------------|
| `LANGFUSE_ENABLED` | `false` | Enable/disable tracing |
| `LANGFUSE_PUBLIC_KEY` | `None` | Langfuse public API key |
| `LANGFUSE_SECRET_KEY` | `None` | Langfuse secret API key |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | Langfuse instance URL |

## Implementation Details

### Callback Handler

The integration uses Langfuse's callback handler which is automatically attached to LangGraph execution:

```python
from intelli.agents.observability import get_langfuse_handler

handler = get_langfuse_handler(
    session_id="abc-123",
    user_id="user-456"
)
callbacks = [handler] if handler else []

# Handler is passed to LangGraph config
lg_config = {
    "configurable": {"thread_id": thread_id},
    "callbacks": callbacks,
}
```

### Trace Grouping

- **Session ID**: Used to group all messages in a conversation
- **User ID**: Optional, used for user-level analytics
- **Run ID**: Each agent execution gets a unique run ID (from the run ledger)

### Performance Impact

- When disabled (`LANGFUSE_ENABLED=false`): Zero overhead
- When enabled: Minimal overhead (~10-50ms per trace)
- Traces are sent asynchronously to avoid blocking the response stream

## Monitoring Best Practices

1. **Development**: Use local Langfuse (docker-compose profile)
2. **Staging**: Use Langfuse Cloud with a staging project
3. **Production**: Use Langfuse Cloud with a separate production project

## Troubleshooting

### Traces not appearing

1. Check `LANGFUSE_ENABLED=true` in your `.env`
2. Verify API keys are correct
3. Check the API server logs for Langfuse errors
4. Ensure `langfuse` package is installed: `pip install -e ".[observability]"`

### Import errors

If you see "No module named 'langfuse'":

```bash
pip install -e ".[observability]"
```

The integration gracefully handles missing langfuse package by returning `None` instead of a handler.

### Docker network issues (local Langfuse)

If using local Langfuse in Docker and traces aren't appearing:

1. Ensure the observability profile is active: `docker compose --profile observability up -d`
2. Check Langfuse is healthy: `docker compose ps langfuse`
3. Try accessing http://localhost:3000 in your browser
4. Check the Langfuse database was initialized: `docker compose logs langfuse | grep -i database`

## Related

- Langfuse Documentation: https://langfuse.com/docs
- LangGraph Callbacks: https://python.langchain.com/docs/modules/callbacks/
- ADR-005: Agent Framework Selection (LangGraph)
