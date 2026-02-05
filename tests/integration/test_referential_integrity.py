"""Referential integrity tests for the DB FK graph.

Verify that foreign key constraints are enforced and that related
entities can be created/queried through valid FK chains.

Requires Docker services running (postgres).
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from intelli.db.models.runs import Run, RunEvent, RunEventType, RunStatus
from intelli.db.models.substrate import Manifest

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Manifest FK tests
# ---------------------------------------------------------------------------


class TestManifestFK:
    @pytest.mark.asyncio
    async def test_run_with_nonexistent_manifest_fails(self, test_session):
        """Creating a Run referencing a non-existent manifest raises IntegrityError."""
        run = Run(
            run_type="agent_chat",
            name="Test",
            status=RunStatus.PENDING.value,
            input_manifest_sha256="0" * 64,
        )
        test_session.add(run)
        with pytest.raises(IntegrityError):
            await test_session.flush()

    @pytest.mark.asyncio
    async def test_run_with_valid_manifest_succeeds(self, test_session):
        """Creating a Run with a valid manifest_sha256 succeeds."""
        sha = "b" * 64
        test_session.add(
            Manifest(sha256=sha, tree={"entries": []}, entry_count=0, total_size_bytes=0)
        )
        await test_session.flush()

        run = Run(
            run_type="agent_chat",
            name="Test",
            status=RunStatus.PENDING.value,
            input_manifest_sha256=sha,
        )
        test_session.add(run)
        await test_session.flush()

        assert run.id is not None
        assert run.input_manifest_sha256 == sha

    @pytest.mark.asyncio
    async def test_manifest_parent_chain(self, test_session):
        """A manifest can reference a parent manifest via parent_sha256."""
        parent_sha = "c" * 64
        child_sha = "d" * 64
        test_session.add(
            Manifest(sha256=parent_sha, tree={"entries": []}, entry_count=0, total_size_bytes=0)
        )
        await test_session.flush()

        child = Manifest(
            sha256=child_sha,
            tree={"entries": ["new"]},
            entry_count=1,
            total_size_bytes=100,
            parent_sha256=parent_sha,
        )
        test_session.add(child)
        await test_session.flush()

        assert child.parent_sha256 == parent_sha

    @pytest.mark.asyncio
    async def test_manifest_invalid_parent_fails(self, test_session):
        """A manifest referencing a non-existent parent raises IntegrityError."""
        child = Manifest(
            sha256="e" * 64,
            tree={"entries": []},
            entry_count=0,
            total_size_bytes=0,
            parent_sha256="1" * 64,
        )
        test_session.add(child)
        with pytest.raises(IntegrityError):
            await test_session.flush()


# ---------------------------------------------------------------------------
# RunEvent FK tests
# ---------------------------------------------------------------------------


class TestRunEventFK:
    @pytest.mark.asyncio
    async def test_run_event_with_nonexistent_run_fails(self, test_session):
        """Creating a RunEvent for a non-existent run raises IntegrityError."""
        event = RunEvent(
            run_id=uuid4(),
            event_type=RunEventType.STEP_STARTED.value,
            payload={"step": "retrieve"},
            sequence_num=1,
        )
        test_session.add(event)
        with pytest.raises(IntegrityError):
            await test_session.flush()

    @pytest.mark.asyncio
    async def test_run_event_with_valid_run_succeeds(self, test_session):
        """Creating a RunEvent for an existing run succeeds."""
        sha = "f" * 64
        test_session.add(
            Manifest(sha256=sha, tree={"entries": []}, entry_count=0, total_size_bytes=0)
        )
        await test_session.flush()

        run = Run(
            run_type="agent_chat",
            name="Test",
            status=RunStatus.PENDING.value,
            input_manifest_sha256=sha,
        )
        test_session.add(run)
        await test_session.flush()

        event = RunEvent(
            run_id=run.id,
            event_type=RunEventType.STEP_STARTED.value,
            payload={"step": "retrieve"},
            sequence_num=1,
        )
        test_session.add(event)
        await test_session.flush()

        assert event.id is not None
        assert event.run_id == run.id
