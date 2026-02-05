"""PostgreSQL LISTEN/NOTIFY pub/sub for real-time events.

Provides true real-time updates without polling by leveraging
PostgreSQL's native LISTEN/NOTIFY mechanism.

Usage:
    # Publisher (in services after database changes)
    await pubsub.publish("run_events", {"run_id": "...", "event": "..."})

    # Subscriber (in SSE endpoints)
    async for message in pubsub.subscribe("run_events"):
        yield f"data: {message}\n\n"
"""

import asyncio
import json
from collections import defaultdict
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress

import asyncpg

from intelli.config import settings


class PubSub:
    """PostgreSQL LISTEN/NOTIFY based pub/sub system.

    Provides a simple interface for publishing and subscribing to channels.
    Much more efficient than polling - notifications are pushed immediately.
    """

    def __init__(self):
        self._connection: asyncpg.Connection | None = None
        self._listeners: dict[str, set[asyncio.Queue]] = defaultdict(set)
        self._listen_task: asyncio.Task | None = None
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        """Establish connection to PostgreSQL for LISTEN."""
        if self._connection is not None:
            return

        # Parse the SQLAlchemy URL to get asyncpg connection params
        db_url = str(settings.database_url)
        # Convert from postgresql+asyncpg:// to postgresql://
        asyncpg_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

        self._connection = await asyncpg.connect(asyncpg_url)

        # Start the listener task
        self._listen_task = asyncio.create_task(self._listen_loop())

    async def disconnect(self) -> None:
        """Close the connection."""
        if self._listen_task:
            self._listen_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._listen_task

        if self._connection:
            await self._connection.close()
            self._connection = None

    async def _listen_loop(self) -> None:
        """Background task that receives notifications and dispatches to subscribers."""
        if not self._connection:
            return

        def notification_handler(connection, pid, channel, payload):
            """Handle incoming notifications."""
            # Dispatch to all queues subscribed to this channel
            if channel in self._listeners:
                for queue in self._listeners[channel]:
                    try:
                        queue.put_nowait(payload)
                    except asyncio.QueueFull:
                        pass  # Drop if queue is full

        # Register the handler
        await self._connection.add_listener("run_events", notification_handler)
        await self._connection.add_listener("activity", notification_handler)
        await self._connection.add_listener("pointer_changes", notification_handler)

        # Keep the task alive
        while True:
            await asyncio.sleep(1)

    async def publish(self, channel: str, data: dict) -> None:
        """Publish a message to a channel.

        Args:
            channel: Channel name (e.g., "run_events", "activity")
            data: Data to publish (will be JSON-encoded)
        """
        if not self._connection:
            await self.connect()

        payload = json.dumps(data)

        # NOTIFY has a payload limit of ~8000 bytes
        # For larger payloads, store in DB and send reference
        if len(payload) > 7500:
            # Truncate or send reference
            payload = json.dumps(
                {
                    "type": "large_payload",
                    "channel": channel,
                    "message": "Payload too large, fetch from API",
                }
            )

        await self._connection.execute(f"NOTIFY {channel}, $1", payload)

    async def subscribe(self, channel: str) -> AsyncGenerator[str, None]:
        """Subscribe to a channel and yield messages.

        Args:
            channel: Channel name to subscribe to

        Yields:
            JSON-encoded messages as they arrive
        """
        if not self._connection:
            await self.connect()

        # Create a queue for this subscriber
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)

        async with self._lock:
            # Add LISTEN for this channel if not already listening
            if channel not in self._listeners or not self._listeners[channel]:
                await self._connection.execute(f"LISTEN {channel}")
            self._listeners[channel].add(queue)

        try:
            while True:
                try:
                    # Wait for message with timeout for keepalive
                    message = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield message
                except TimeoutError:
                    # Send heartbeat
                    yield json.dumps({"type": "heartbeat"})
        finally:
            # Cleanup on disconnect
            async with self._lock:
                self._listeners[channel].discard(queue)
                if not self._listeners[channel]:
                    await self._connection.execute(f"UNLISTEN {channel}")

    @asynccontextmanager
    async def subscription(self, channel: str):
        """Context manager for subscriptions.

        Usage:
            async with pubsub.subscription("run_events") as messages:
                async for msg in messages:
                    print(msg)
        """
        gen = self.subscribe(channel)
        try:
            yield gen
        finally:
            await gen.aclose()


# Global pubsub instance
pubsub = PubSub()


async def get_pubsub() -> PubSub:
    """Get the global pubsub instance, connecting if needed."""
    if pubsub._connection is None:
        await pubsub.connect()
    return pubsub
