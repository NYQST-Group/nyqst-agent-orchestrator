"""Initial substrate: artifacts, manifests, pointers, runs, run_events.

Revision ID: 20260123_0001
Revises:
Create Date: 2026-01-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260123_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable required extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"pgcrypto\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"vector\"")

    # Create artifacts table
    op.create_table(
        "artifacts",
        sa.Column("sha256", sa.String(64), nullable=False, comment="SHA-256 hash of artifact content"),
        sa.Column("media_type", sa.String(255), nullable=False, comment="MIME type (e.g., application/pdf)"),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False, comment="Content size in bytes"),
        sa.Column("filename", sa.String(1024), nullable=True, comment="Original filename"),
        sa.Column("storage_uri", sa.String(2048), nullable=False, comment="Storage URI (e.g., s3://bucket/key)"),
        sa.Column("storage_class", sa.String(50), nullable=False, server_default="STANDARD", comment="Storage class"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True, comment="Principal ID who created this artifact"),
        sa.Column("reference_count", sa.Integer(), nullable=False, server_default="1", comment="Number of manifests referencing this artifact"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("sha256", name=op.f("pk_artifacts")),
        sa.CheckConstraint("sha256 ~ '^[a-f0-9]{64}$'", name="ck_artifacts_sha256_format"),
    )
    op.create_index("ix_artifacts_media_type", "artifacts", ["media_type"])
    op.create_index("ix_artifacts_created_at", "artifacts", ["created_at"])

    # Create manifests table
    op.create_table(
        "manifests",
        sa.Column("sha256", sa.String(64), nullable=False, comment="SHA-256 hash of canonical JSON tree"),
        sa.Column("tree", postgresql.JSONB(), nullable=False, comment="Tree structure with entries and metadata"),
        sa.Column("parent_sha256", sa.String(64), nullable=True, comment="Parent manifest SHA-256 for history chain"),
        sa.Column("entry_count", sa.Integer(), nullable=False, comment="Number of entries in this manifest"),
        sa.Column("total_size_bytes", sa.BigInteger(), nullable=False, comment="Total size of all referenced artifacts"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True, comment="Principal ID who created this manifest"),
        sa.Column("message", sa.Text(), nullable=True, comment="Commit message describing this snapshot"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("sha256", name=op.f("pk_manifests")),
        sa.ForeignKeyConstraint(["parent_sha256"], ["manifests.sha256"], name=op.f("fk_manifests_parent_sha256_manifests")),
        sa.CheckConstraint("sha256 ~ '^[a-f0-9]{64}$'", name="ck_manifests_sha256_format"),
    )
    op.create_index("ix_manifests_parent", "manifests", ["parent_sha256"])
    op.create_index("ix_manifests_created_at", "manifests", ["created_at"])
    op.create_index("ix_manifests_tree", "manifests", ["tree"], postgresql_using="gin")

    # Create pointers table
    op.create_table(
        "pointers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("namespace", sa.String(255), nullable=False, server_default="default", comment="Namespace for pointer"),
        sa.Column("name", sa.String(255), nullable=False, comment="Pointer name within namespace"),
        sa.Column("manifest_sha256", sa.String(64), nullable=True, comment="Current HEAD manifest SHA-256"),
        sa.Column("pointer_type", sa.String(50), nullable=False, server_default="bundle", comment="Type: bundle, corpus, snapshot"),
        sa.Column("description", sa.Text(), nullable=True, comment="Human-readable description"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True, comment="Principal ID who created this pointer"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_pointers")),
        sa.ForeignKeyConstraint(["manifest_sha256"], ["manifests.sha256"], name=op.f("fk_pointers_manifest_sha256_manifests")),
        sa.UniqueConstraint("namespace", "name", "deleted_at", name="uq_pointer_name"),
    )
    op.create_index("ix_pointers_namespace", "pointers", ["namespace"], postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("ix_pointers_type", "pointers", ["pointer_type"], postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("ix_pointers_manifest", "pointers", ["manifest_sha256"])

    # Create pointer_history table
    op.create_table(
        "pointer_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("pointer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("old_sha256", sa.String(64), nullable=True, comment="Previous manifest SHA-256"),
        sa.Column("new_sha256", sa.String(64), nullable=True, comment="New manifest SHA-256"),
        sa.Column("operation", sa.String(50), nullable=False, comment="Operation: create, advance, reset, revert"),
        sa.Column("changed_by", postgresql.UUID(as_uuid=True), nullable=True, comment="Principal ID who made the change"),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("reason", sa.Text(), nullable=True, comment="Reason for the change"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_pointer_history")),
        sa.ForeignKeyConstraint(["pointer_id"], ["pointers.id"], name=op.f("fk_pointer_history_pointer_id_pointers")),
    )
    op.create_index("ix_pointer_history_pointer", "pointer_history", ["pointer_id", "changed_at"])

    # Create runs table
    op.create_table(
        "runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("run_type", sa.String(100), nullable=False, comment="Run type: document_parse, research, analysis, etc."),
        sa.Column("name", sa.String(255), nullable=True, comment="Human-readable run name"),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending", comment="Current run status"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True, comment="When the run started executing"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True, comment="When the run completed"),
        sa.Column("input_manifest_sha256", sa.String(64), nullable=True, comment="Input manifest SHA-256"),
        sa.Column("output_manifest_sha256", sa.String(64), nullable=True, comment="Output manifest SHA-256"),
        sa.Column("config", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("result", postgresql.JSONB(), nullable=True),
        sa.Column("error", postgresql.JSONB(), nullable=True),
        sa.Column("token_usage", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("cost_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("parent_run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_runs")),
        sa.ForeignKeyConstraint(["input_manifest_sha256"], ["manifests.sha256"], name=op.f("fk_runs_input_manifest_sha256_manifests")),
        sa.ForeignKeyConstraint(["output_manifest_sha256"], ["manifests.sha256"], name=op.f("fk_runs_output_manifest_sha256_manifests")),
        sa.ForeignKeyConstraint(["parent_run_id"], ["runs.id"], name=op.f("fk_runs_parent_run_id_runs")),
    )
    op.create_index("ix_runs_status", "runs", ["status"])
    op.create_index("ix_runs_type", "runs", ["run_type"])
    op.create_index("ix_runs_created_at", "runs", ["created_at"])
    op.create_index("ix_runs_project", "runs", ["project_id"], postgresql_where=sa.text("project_id IS NOT NULL"))

    # Create run_events table
    op.create_table(
        "run_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False, comment="Monotonic event ID"),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False, comment="Event type from RunEventType enum"),
        sa.Column("payload", postgresql.JSONB(), nullable=False, comment="Event-specific payload data"),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("duration_ms", sa.Integer(), nullable=True, comment="Duration in milliseconds"),
        sa.Column("sequence_num", sa.Integer(), nullable=False, comment="Sequence number within the run"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_run_events")),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"], name=op.f("fk_run_events_run_id_runs")),
        sa.UniqueConstraint("run_id", "sequence_num", name="uq_run_event_sequence"),
    )
    op.create_index("ix_run_events_run", "run_events", ["run_id", "sequence_num"])
    op.create_index("ix_run_events_type", "run_events", ["event_type"])
    op.create_index("ix_run_events_timestamp", "run_events", ["timestamp"])


def downgrade() -> None:
    op.drop_table("run_events")
    op.drop_table("runs")
    op.drop_table("pointer_history")
    op.drop_table("pointers")
    op.drop_table("manifests")
    op.drop_table("artifacts")
