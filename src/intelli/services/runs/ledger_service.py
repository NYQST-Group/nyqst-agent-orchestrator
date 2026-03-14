"""Service for run ledger (event logging) operations."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from intelli.db.models.runs import RunEvent
from intelli.repositories.runs import RunEventRepository


class LedgerService:
    """Service for run ledger (append-only event log).

    Provides methods for logging various event types and
    querying event history. Events are automatically published
    via PostgreSQL NOTIFY for real-time streaming.
    """

    def __init__(self, session: AsyncSession, publish_events: bool = True):
        """Initialize ledger service.

        Args:
            session: Database session
            publish_events: Whether to publish events via NOTIFY
        """
        self.session = session
        self.repo = RunEventRepository(session)
        self._publish_events = publish_events

    async def log_event(
        self,
        run_id: UUID,
        event_type: str,
        payload: dict,
        duration_ms: int | None = None,
    ) -> RunEvent:
        """Log a generic event.

        Args:
            run_id: Run ID
            event_type: Event type
            payload: Event payload
            duration_ms: Duration in milliseconds

        Returns:
            Created event
        """
        event = await self.repo.append_event(
            run_id=run_id,
            event_type=event_type,
            payload=payload,
            duration_ms=duration_ms,
        )

        # Publish via PostgreSQL NOTIFY for real-time subscribers
        if self._publish_events:
            await self._publish_event(event)

        return event

    async def _publish_event(self, event: RunEvent) -> None:
        """Publish event via PostgreSQL NOTIFY.

        Uses the raw connection to send NOTIFY, which is picked up
        by any listening SSE connections.

        Note: PostgreSQL NOTIFY has an 8000 byte limit. Large payloads
        are truncated or skipped to avoid errors.
        """
        import json

        from sqlalchemy import text

        notification_payload = json.dumps(
            {
                "id": event.id,
                "run_id": str(event.run_id),
                "event_type": event.event_type,
                "payload": event.payload,
                "timestamp": event.timestamp.isoformat(),
                "duration_ms": event.duration_ms,
                "sequence_num": event.sequence_num,
            }
        )

        # PostgreSQL NOTIFY has 8000 byte limit - skip large payloads
        if len(notification_payload) > 7500:
            # Send a truncated notification without full payload
            notification_payload = json.dumps(
                {
                    "id": event.id,
                    "run_id": str(event.run_id),
                    "event_type": event.event_type,
                    "payload": {"_truncated": True, "event_type": event.event_type},
                    "timestamp": event.timestamp.isoformat(),
                    "duration_ms": event.duration_ms,
                    "sequence_num": event.sequence_num,
                }
            )

        # PostgreSQL NOTIFY - received by any LISTEN connections
        await self.session.execute(
            text("SELECT pg_notify('run_events', :payload)"), {"payload": notification_payload}
        )

    async def log_step_start(
        self,
        run_id: UUID,
        step_name: str,
        input_data: dict | None = None,
    ) -> RunEvent:
        """Log step start.

        Args:
            run_id: Run ID
            step_name: Step name
            input_data: Input to the step

        Returns:
            Created event
        """
        return await self.log_event(
            run_id=run_id,
            event_type="step_started",
            payload={
                "step_name": step_name,
                "input_data": input_data,
            },
        )

    async def log_step_complete(
        self,
        run_id: UUID,
        step_name: str,
        output_data: dict | None = None,
        duration_ms: int | None = None,
        success: bool = True,
    ) -> RunEvent:
        """Log step completion.

        Args:
            run_id: Run ID
            step_name: Step name
            output_data: Output from the step
            duration_ms: Duration in milliseconds
            success: Whether step succeeded

        Returns:
            Created event
        """
        return await self.log_event(
            run_id=run_id,
            event_type="step_completed",
            payload={
                "step_name": step_name,
                "output_data": output_data,
                "success": success,
            },
            duration_ms=duration_ms,
        )

    async def log_tool_call_start(
        self,
        run_id: UUID,
        tool_name: str,
        arguments: dict,
        tool_version: str | None = None,
    ) -> RunEvent:
        """Log tool call start.

        Args:
            run_id: Run ID
            tool_name: Tool name
            arguments: Tool arguments
            tool_version: Tool version

        Returns:
            Created event
        """
        return await self.log_event(
            run_id=run_id,
            event_type="tool_call_started",
            payload={
                "tool_name": tool_name,
                "tool_version": tool_version,
                "arguments": arguments,
            },
        )

    async def log_tool_call_complete(
        self,
        run_id: UUID,
        tool_name: str,
        result: dict | None = None,
        duration_ms: int | None = None,
    ) -> RunEvent:
        """Log tool call completion.

        Args:
            run_id: Run ID
            tool_name: Tool name
            result: Tool result
            duration_ms: Duration in milliseconds

        Returns:
            Created event
        """
        return await self.log_event(
            run_id=run_id,
            event_type="tool_call_completed",
            payload={
                "tool_name": tool_name,
                "result": result,
            },
            duration_ms=duration_ms,
        )

    async def log_llm_request(
        self,
        run_id: UUID,
        model: str,
        messages: list[dict],
        input_tokens: int | None = None,
    ) -> RunEvent:
        """Log LLM request.

        Args:
            run_id: Run ID
            model: Model ID
            messages: Input messages
            input_tokens: Input token count

        Returns:
            Created event
        """
        return await self.log_event(
            run_id=run_id,
            event_type="llm_request",
            payload={
                "model": model,
                "messages": messages,
                "input_tokens": input_tokens,
            },
        )

    async def log_llm_response(
        self,
        run_id: UUID,
        model: str,
        response: dict,
        output_tokens: int | None = None,
        cost_micros: int | None = None,
        duration_ms: int | None = None,
    ) -> RunEvent:
        """Log LLM response.

        Args:
            run_id: Run ID
            model: Model ID
            response: Response content
            output_tokens: Output token count
            duration_ms: Duration in milliseconds

        Returns:
            Created event
        """
        return await self.log_event(
            run_id=run_id,
            event_type="llm_response",
            payload={
                "model": model,
                "response": response,
                "output_tokens": output_tokens,
                "cost_micros": cost_micros,
            },
            duration_ms=duration_ms,
        )

    async def log_retrieval_query(
        self,
        run_id: UUID,
        kb_id: str,
        query: str,
        profile: str | None = None,
    ) -> RunEvent:
        """Log retrieval query.

        Args:
            run_id: Run ID
            kb_id: Knowledge base ID
            query: Query text
            profile: Retrieval profile

        Returns:
            Created event
        """
        return await self.log_event(
            run_id=run_id,
            event_type="retrieval_query",
            payload={
                "kb_id": kb_id,
                "query": query,
                "profile": profile,
            },
        )

    async def log_retrieval_result(
        self,
        run_id: UUID,
        kb_id: str,
        results: list[dict],
        duration_ms: int | None = None,
    ) -> RunEvent:
        """Log retrieval result.

        Args:
            run_id: Run ID
            kb_id: Knowledge base ID
            results: Retrieved results
            duration_ms: Duration in milliseconds

        Returns:
            Created event
        """
        return await self.log_event(
            run_id=run_id,
            event_type="retrieval_result",
            payload={
                "kb_id": kb_id,
                "results": results,
            },
            duration_ms=duration_ms,
        )

    async def log_checkpoint(
        self,
        run_id: UUID,
        state: dict,
        resumable: bool = True,
        checkpoint_id: str | None = None,
    ) -> RunEvent:
        """Log a checkpoint for run resumption.

        Args:
            run_id: Run ID
            state: Serialized state
            resumable: Whether run can be resumed
            checkpoint_id: Checkpoint identifier

        Returns:
            Created event
        """
        return await self.log_event(
            run_id=run_id,
            event_type="checkpoint",
            payload={
                "state": state,
                "resumable": resumable,
                "checkpoint_id": checkpoint_id,
            },
        )

    async def log_artifact_emitted(
        self,
        run_id: UUID,
        artifact_sha256: str,
        path: str | None = None,
    ) -> RunEvent:
        """Log artifact emission.

        Args:
            run_id: Run ID
            artifact_sha256: Artifact SHA-256
            path: Path within output

        Returns:
            Created event
        """
        return await self.log_event(
            run_id=run_id,
            event_type="artifact_emitted",
            payload={
                "artifact_sha256": artifact_sha256,
                "path": path,
            },
        )

    async def log_error(
        self,
        run_id: UUID,
        error_type: str,
        message: str,
        details: dict | None = None,
    ) -> RunEvent:
        """Log an error.

        Args:
            run_id: Run ID
            error_type: Error type
            message: Error message
            details: Additional details

        Returns:
            Created event
        """
        return await self.log_event(
            run_id=run_id,
            event_type="error",
            payload={
                "error_type": error_type,
                "message": message,
                "details": details,
            },
        )

    async def get_events(
        self,
        run_id: UUID,
        event_types: list[str] | None = None,
        since_sequence: int | None = None,
        limit: int = 1000,
    ) -> list[RunEvent]:
        """Get events for a run.

        Args:
            run_id: Run ID
            event_types: Filter by event types
            since_sequence: Get events after this sequence
            limit: Maximum records

        Returns:
            List of events
        """
        return await self.repo.get_events_for_run(
            run_id=run_id,
            event_types=event_types,
            since_sequence=since_sequence,
            limit=limit,
        )

    async def get_latest_checkpoint(self, run_id: UUID) -> RunEvent | None:
        """Get the most recent checkpoint.

        Args:
            run_id: Run ID

        Returns:
            Checkpoint event or None
        """
        return await self.repo.get_latest_checkpoint(run_id)

    async def count_events(self, run_id: UUID) -> int:
        """Count events for a run.

        Args:
            run_id: Run ID

        Returns:
            Event count
        """
        return await self.repo.count_by_run(run_id)
