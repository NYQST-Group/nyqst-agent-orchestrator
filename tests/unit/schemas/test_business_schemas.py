"""Unit tests for thin business-surface contract schemas."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from intelli.schemas.business import (
    ClientCreate,
    ClientListResponse,
    DashboardSummaryResponse,
    DecisionCreate,
    DecisionListResponse,
    DecisionResponse,
    DecisionStatus,
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectStatus,
)

pytestmark = pytest.mark.unit


class TestProjectCreate:
    def test_project_create_defaults(self):
        data = ProjectCreate.model_validate({"name": "Sample Lease Review"})
        assert data.name == "Sample Lease Review"
        assert data.objective is None
        assert data.status == ProjectStatus.ACTIVE
        assert data.client_id is None

    def test_project_create_extra_field_rejected(self):
        with pytest.raises(ValidationError) as exc_info:
            ProjectCreate.model_validate({"name": "Sample Lease Review", "bad": "field"})
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestClientCreate:
    def test_client_create_defaults(self):
        data = ClientCreate.model_validate({"name": "Acme Capital"})
        assert data.name == "Acme Capital"
        assert data.description is None
        assert data.status.value == "active"


class TestDecisionCreate:
    def test_decision_create_defaults(self):
        data = DecisionCreate.model_validate(
            {
                "project_id": uuid4(),
                "title": "Approve lease position",
                "decision": "Proceed with the revised clause set.",
                "rationale": "The change resolves the material risk.",
            }
        )
        assert data.status == DecisionStatus.DRAFT
        assert data.citations == []
        assert data.linked_artifacts == []
        assert data.stale is False
        assert data.stale_reason is None

    def test_decision_create_rejects_unknown_fields(self):
        with pytest.raises(ValidationError) as exc_info:
            DecisionCreate.model_validate(
                {
                    "project_id": uuid4(),
                    "title": "Approve lease position",
                    "decision": "Proceed",
                    "rationale": "Why",
                    "bad": "field",
                }
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestBusinessResponses:
    def test_project_response_supports_nested_refs(self):
        now = datetime.now(UTC)
        project_id = uuid4()
        client_id = uuid4()
        decision_id = uuid4()
        pointer_id = uuid4()

        data = ProjectResponse.model_validate(
            {
                "id": project_id,
                "name": "Sample Lease Review",
                "objective": "Resolve high-risk clauses before buyer review.",
                "status": "active",
                "client": {"id": client_id, "name": "Acme Capital"},
                "primary_bundle": {
                    "pointer_id": pointer_id,
                    "name": "Lease Review Bundle",
                    "manifest_sha256": "abc123",
                    "updated_at": now,
                },
                "last_activity_at": now,
                "active_run_count": 1,
                "bundle_count": 2,
                "research_pack_count": 1,
                "decision_count": 1,
                "stale_decision_count": 0,
                "recent_decisions": [
                    {
                        "id": decision_id,
                        "title": "Approve lease position",
                        "status": "approved",
                        "stale": False,
                    }
                ],
                "created_at": now,
                "updated_at": now,
                "created_by": uuid4(),
                "created_by_name": "M. Forster",
            }
        )
        assert data.id == project_id
        assert data.client is not None
        assert data.client.id == client_id
        assert data.primary_bundle is not None
        assert data.primary_bundle.pointer_id == pointer_id
        assert data.recent_decisions[0].id == decision_id

    def test_dashboard_summary_validates_nested_sections(self):
        now = datetime.now(UTC)
        project_id = uuid4()
        decision_id = uuid4()
        run_id = uuid4()

        data = DashboardSummaryResponse.model_validate(
            {
                "generated_at": now,
                "counts": {
                    "active_run_count": 1,
                    "project_count": 2,
                    "client_count": 1,
                    "decision_count": 3,
                    "stale_decision_count": 1,
                },
                "active_runs": [
                    {
                        "id": run_id,
                        "name": "Lease review run",
                        "run_type": "analysis",
                        "status": "running",
                        "project": {
                            "id": project_id,
                            "name": "Sample Lease Review",
                            "status": "active",
                        },
                        "updated_at": now,
                    }
                ],
                "workflow_activity": [
                    {
                        "id": "activity-1",
                        "title": "Bundle prepared for review",
                        "status": "completed",
                        "occurred_at": now,
                        "project": {
                            "id": project_id,
                            "name": "Sample Lease Review",
                            "status": "active",
                        },
                    }
                ],
                "recent_bundle_changes": [
                    {
                        "pointer_id": uuid4(),
                        "bundle_name": "Lease Review Bundle",
                        "manifest_sha256": "abc123",
                        "changed_at": now,
                        "project": {
                            "id": project_id,
                            "name": "Sample Lease Review",
                            "status": "active",
                        },
                    }
                ],
                "recent_research_packs": [
                    {
                        "id": "pack-1",
                        "name": "Lease Position Pack",
                        "updated_at": now,
                        "project": {
                            "id": project_id,
                            "name": "Sample Lease Review",
                            "status": "active",
                        },
                    }
                ],
                "key_projects": [
                    {
                        "id": project_id,
                        "name": "Sample Lease Review",
                        "objective": "Resolve high-risk clauses before buyer review.",
                        "status": "active",
                        "client": None,
                        "primary_bundle": None,
                        "last_activity_at": now,
                        "active_run_count": 1,
                        "bundle_count": 2,
                        "research_pack_count": 1,
                        "decision_count": 1,
                        "stale_decision_count": 0,
                        "recent_decisions": [],
                        "created_at": now,
                        "updated_at": now,
                        "created_by": None,
                        "created_by_name": None,
                    }
                ],
                "recent_decisions": [
                    {
                        "id": decision_id,
                        "project": {
                            "id": project_id,
                            "name": "Sample Lease Review",
                            "status": "active",
                        },
                        "title": "Approve lease position",
                        "decision": "Proceed with the revised clause set.",
                        "rationale": "The change resolves the material risk.",
                        "status": "approved",
                        "citations": [],
                        "linked_artifacts": [],
                        "stale": False,
                        "stale_reason": None,
                        "created_at": now,
                        "updated_at": now,
                        "created_by": None,
                        "created_by_name": "M. Forster",
                    }
                ],
                "attention_items": [
                    {
                        "id": "decision:1",
                        "item_type": "decision",
                        "title": "Lease position needs refresh",
                        "reason": "Underlying evidence changed",
                        "severity": "warning",
                        "occurred_at": now,
                        "project": {
                            "id": project_id,
                            "name": "Sample Lease Review",
                            "status": "active",
                        },
                    }
                ],
            }
        )

        assert data.counts.project_count == 2
        assert data.active_runs[0].project is not None
        assert data.recent_decisions[0].status == DecisionStatus.APPROVED
        assert data.attention_items[0].severity.value == "warning"

    def test_decision_response_preserves_thin_evidence_refs(self):
        now = datetime.now(UTC)
        project_id = uuid4()
        decision = DecisionResponse.model_validate(
            {
                "id": uuid4(),
                "project": {
                    "id": project_id,
                    "name": "Sample Lease Review",
                    "status": "active",
                },
                "title": "Approve lease position",
                "decision": "Proceed with the revised clause set.",
                "rationale": "The change resolves the material risk.",
                "status": "approved",
                "citations": [
                    {
                        "source_type": "bundle",
                        "source_id": "bundle:lease-review",
                        "label": "Lease review bundle",
                        "locator": "p.12",
                        "href": "/docs/lease-review",
                    }
                ],
                "linked_artifacts": [
                    {
                        "artifact_sha256": "abc123",
                        "label": "Lease diff",
                        "media_type": "application/pdf",
                        "href": "/artifacts/abc123",
                    }
                ],
                "stale": False,
                "stale_reason": None,
                "created_at": now,
                "updated_at": now,
                "created_by": None,
                "created_by_name": "M. Forster",
            }
        )

        assert decision.project.id == project_id
        assert decision.citations[0].source_type == "bundle"
        assert decision.linked_artifacts[0].artifact_sha256 == "abc123"

    def test_list_responses_lock_pagination_shape(self):
        project_list = ProjectListResponse.model_validate(
            {"items": [], "total": 0, "limit": 25, "offset": 0}
        )
        client_list = ClientListResponse.model_validate(
            {"items": [], "total": 0, "limit": 25, "offset": 0}
        )
        decision_list = DecisionListResponse.model_validate(
            {"items": [], "total": 0, "limit": 25, "offset": 0}
        )

        assert project_list.limit == 25
        assert client_list.offset == 0
        assert decision_list.total == 0
