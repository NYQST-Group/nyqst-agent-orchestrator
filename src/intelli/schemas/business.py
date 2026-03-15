"""Thin business-surface contract schemas for D2 dashboard and buyer-facing records."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _validate_sha256(value: str | None, field_name: str) -> str | None:
    """Validate and normalize SHA-256 identifiers."""
    if value is None:
        return value
    if len(value) != 64:
        raise ValueError(f"{field_name} must be a 64-character hex string")
    try:
        int(value, 16)
    except ValueError:
        raise ValueError(f"{field_name} must be a valid hex string")
    return value.lower()


class ProjectStatus(StrEnum):
    """Thin project lifecycle states."""

    ACTIVE = "active"
    AT_RISK = "at_risk"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ClientStatus(StrEnum):
    """Thin client lifecycle states."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class DecisionStatus(StrEnum):
    """Buyer-facing decision states."""

    DRAFT = "draft"
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class DashboardAttentionSeverity(StrEnum):
    """How strongly the dashboard should surface an attention item."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ClientRef(BaseModel):
    """Thin client reference embedded in related records."""

    id: UUID = Field(..., description="Client ID")
    name: str = Field(..., description="Buyer-facing client name")

    model_config = ConfigDict(from_attributes=True)


class ProjectRef(BaseModel):
    """Thin project reference embedded in related records."""

    id: UUID = Field(..., description="Project ID")
    name: str = Field(..., description="Buyer-facing project name")
    status: ProjectStatus = Field(..., description="Current project status")

    model_config = ConfigDict(from_attributes=True)


class DecisionRef(BaseModel):
    """Thin decision reference embedded in related records."""

    id: UUID = Field(..., description="Decision ID")
    title: str = Field(..., description="Decision title")
    status: DecisionStatus = Field(..., description="Current decision status")
    stale: bool = Field(False, description="Whether the decision is marked stale")

    model_config = ConfigDict(from_attributes=True)


class BundleRef(BaseModel):
    """Buyer-facing bundle reference over the pointer/notebook substrate."""

    pointer_id: UUID = Field(..., description="Backing pointer ID")
    name: str = Field(..., description="Buyer-facing bundle name")
    manifest_sha256: str | None = Field(None, description="Current manifest reference")
    updated_at: datetime | None = Field(None, description="Last bundle update time")

    model_config = ConfigDict(from_attributes=True)

    @field_validator("manifest_sha256")
    @classmethod
    def validate_manifest_sha256(cls, value: str | None) -> str | None:
        """Validate manifest SHA-256 format if provided."""
        return _validate_sha256(value, "manifest_sha256")


class DecisionCitationRef(BaseModel):
    """Thin citation reference for D2 decisions."""

    source_type: str = Field(
        ...,
        description="Thin source label such as bundle, artifact, research_pack, or external_url",
    )
    source_id: str = Field(..., description="Opaque source identifier")
    label: str = Field(..., description="Buyer-readable citation label")
    locator: str | None = Field(None, description="Passage, page, or section locator")
    href: str | None = Field(None, description="Optional URL or app route for opening the source")

    model_config = ConfigDict(extra="forbid")


class DecisionArtifactRef(BaseModel):
    """Thin artifact reference for D2 decisions."""

    artifact_sha256: str = Field(..., description="Artifact SHA-256")
    label: str = Field(..., description="Buyer-readable artifact label")
    media_type: str | None = Field(None, description="Artifact media type")
    href: str | None = Field(None, description="Optional URL or app route for opening the artifact")

    model_config = ConfigDict(extra="forbid")

    @field_validator("artifact_sha256")
    @classmethod
    def validate_artifact_sha256(cls, value: str) -> str:
        """Validate artifact SHA-256 format."""
        normalized = _validate_sha256(value, "artifact_sha256")
        assert normalized is not None
        return normalized


class ProjectCreate(BaseModel):
    """Payload for creating a thin project."""

    name: str = Field(..., min_length=1, max_length=200, description="Buyer-facing project name")
    objective: str | None = Field(
        None,
        max_length=2000,
        description="Short statement of why the project exists",
    )
    status: ProjectStatus = Field(ProjectStatus.ACTIVE, description="Current project status")
    client_id: UUID | None = Field(None, description="Owning client, when known")

    model_config = ConfigDict(extra="forbid")


class ProjectUpdate(BaseModel):
    """Payload for updating a thin project."""

    name: str | None = Field(None, min_length=1, max_length=200, description="Project name")
    objective: str | None = Field(None, max_length=2000, description="Project objective")
    status: ProjectStatus | None = Field(None, description="Current project status")
    client_id: UUID | None = Field(None, description="Owning client, when known")

    model_config = ConfigDict(extra="forbid")


class ProjectResponse(BaseModel):
    """Thin project response for list and detail use cases."""

    id: UUID = Field(..., description="Project ID")
    name: str = Field(..., description="Buyer-facing project name")
    objective: str | None = Field(None, description="Short statement of why the project exists")
    status: ProjectStatus = Field(..., description="Current project status")
    client: ClientRef | None = Field(None, description="Owning client, when known")
    primary_bundle: BundleRef | None = Field(
        None,
        description="Pinned or primary bundle/notebook for the project",
    )
    last_activity_at: datetime | None = Field(None, description="Most recent project activity")
    active_run_count: int = Field(0, ge=0, description="Current active runs scoped to the project")
    bundle_count: int = Field(0, ge=0, description="Visible bundles or notebooks")
    research_pack_count: int = Field(0, ge=0, description="Visible research packs")
    decision_count: int = Field(0, ge=0, description="Visible decision records")
    stale_decision_count: int = Field(0, ge=0, description="Decisions marked stale")
    recent_decisions: list[DecisionRef] = Field(
        default_factory=list,
        description="Optional recent decision slice for project detail",
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: UUID | None = Field(None, description="Creator principal ID")
    created_by_name: str | None = Field(None, description="Creator display name")

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """List response for thin projects."""

    items: list[ProjectResponse] = Field(..., description="Projects")
    total: int = Field(..., ge=0, description="Total project count")
    limit: int = Field(..., ge=1, description="Page size")
    offset: int = Field(..., ge=0, description="Page offset")


class ClientCreate(BaseModel):
    """Payload for creating a thin client."""

    name: str = Field(..., min_length=1, max_length=200, description="Buyer-facing client name")
    description: str | None = Field(
        None,
        max_length=2000,
        description="Short client context or engagement summary",
    )
    status: ClientStatus = Field(ClientStatus.ACTIVE, description="Current client status")

    model_config = ConfigDict(extra="forbid")


class ClientUpdate(BaseModel):
    """Payload for updating a thin client."""

    name: str | None = Field(None, min_length=1, max_length=200, description="Client name")
    description: str | None = Field(None, max_length=2000, description="Client summary")
    status: ClientStatus | None = Field(None, description="Current client status")

    model_config = ConfigDict(extra="forbid")


class ClientResponse(BaseModel):
    """Thin client response for list and detail use cases."""

    id: UUID = Field(..., description="Client ID")
    name: str = Field(..., description="Buyer-facing client name")
    description: str | None = Field(None, description="Short client context or engagement summary")
    status: ClientStatus = Field(..., description="Current client status")
    project_count: int = Field(0, ge=0, description="Projects linked to this client")
    active_project_count: int = Field(0, ge=0, description="Active linked projects")
    decision_count: int = Field(0, ge=0, description="Visible decisions across linked projects")
    last_activity_at: datetime | None = Field(None, description="Most recent client activity")
    recent_projects: list[ProjectRef] = Field(
        default_factory=list,
        description="Optional recent project slice for client detail",
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: UUID | None = Field(None, description="Creator principal ID")
    created_by_name: str | None = Field(None, description="Creator display name")

    model_config = ConfigDict(from_attributes=True)


class ClientListResponse(BaseModel):
    """List response for thin clients."""

    items: list[ClientResponse] = Field(..., description="Clients")
    total: int = Field(..., ge=0, description="Total client count")
    limit: int = Field(..., ge=1, description="Page size")
    offset: int = Field(..., ge=0, description="Page offset")


class DecisionCreate(BaseModel):
    """Payload for creating a thin decision record."""

    project_id: UUID = Field(..., description="Owning project ID")
    title: str = Field(..., min_length=1, max_length=200, description="Decision title")
    decision: str = Field(..., min_length=1, max_length=2000, description="What was decided")
    rationale: str = Field(..., min_length=1, max_length=8000, description="Why it was decided")
    status: DecisionStatus = Field(DecisionStatus.DRAFT, description="Current decision status")
    citations: list[DecisionCitationRef] = Field(
        default_factory=list,
        description="Thin citation references; richer provenance lands later",
    )
    linked_artifacts: list[DecisionArtifactRef] = Field(
        default_factory=list,
        description="Thin linked artifacts; richer provenance lands later",
    )
    stale: bool = Field(False, description="Whether the decision is already marked stale")
    stale_reason: str | None = Field(
        None,
        max_length=1000,
        description="Optional stale or degradation explanation",
    )

    model_config = ConfigDict(extra="forbid")


class DecisionUpdate(BaseModel):
    """Payload for updating a thin decision record."""

    title: str | None = Field(None, min_length=1, max_length=200, description="Decision title")
    decision: str | None = Field(None, min_length=1, max_length=2000, description="Decision text")
    rationale: str | None = Field(None, min_length=1, max_length=8000, description="Rationale")
    status: DecisionStatus | None = Field(None, description="Current decision status")
    citations: list[DecisionCitationRef] | None = Field(
        None,
        description="Thin citation references",
    )
    linked_artifacts: list[DecisionArtifactRef] | None = Field(
        None,
        description="Thin linked artifacts",
    )
    stale: bool | None = Field(None, description="Whether the decision is marked stale")
    stale_reason: str | None = Field(
        None,
        max_length=1000,
        description="Optional stale or degradation explanation",
    )

    model_config = ConfigDict(extra="forbid")


class DecisionResponse(BaseModel):
    """Thin decision response for list and detail use cases."""

    id: UUID = Field(..., description="Decision ID")
    project: ProjectRef = Field(..., description="Owning project")
    title: str = Field(..., description="Decision title")
    decision: str = Field(..., description="What was decided")
    rationale: str = Field(..., description="Why it was decided")
    status: DecisionStatus = Field(..., description="Current decision status")
    citations: list[DecisionCitationRef] = Field(default_factory=list, description="Citations")
    linked_artifacts: list[DecisionArtifactRef] = Field(
        default_factory=list,
        description="Linked artifacts",
    )
    stale: bool = Field(False, description="Whether the decision is marked stale")
    stale_reason: str | None = Field(None, description="Optional stale or degradation explanation")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: UUID | None = Field(None, description="Creator principal ID")
    created_by_name: str | None = Field(None, description="Creator display name")

    model_config = ConfigDict(from_attributes=True)


class DecisionListResponse(BaseModel):
    """List response for thin decisions."""

    items: list[DecisionResponse] = Field(..., description="Decisions")
    total: int = Field(..., ge=0, description="Total decision count")
    limit: int = Field(..., ge=1, description="Page size")
    offset: int = Field(..., ge=0, description="Page offset")


class DashboardCounts(BaseModel):
    """Top-line counts for the dashboard hero cards."""

    active_run_count: int = Field(0, ge=0, description="Runs currently in flight")
    project_count: int = Field(0, ge=0, description="Thin projects in scope")
    client_count: int = Field(0, ge=0, description="Thin clients in scope")
    decision_count: int = Field(0, ge=0, description="Thin decisions in scope")
    stale_decision_count: int = Field(0, ge=0, description="Decisions marked stale")

    model_config = ConfigDict(from_attributes=True)


class DashboardRunSummary(BaseModel):
    """Minimal active-run card for the dashboard."""

    id: UUID = Field(..., description="Run ID")
    name: str | None = Field(None, description="Optional run name")
    run_type: str = Field(..., description="Run type")
    status: str = Field(..., description="Current run status")
    project: ProjectRef | None = Field(None, description="Owning project")
    updated_at: datetime = Field(..., description="Most recent run activity")

    model_config = ConfigDict(from_attributes=True)


class DashboardActivitySummary(BaseModel):
    """Minimal workflow activity card for the dashboard."""

    id: str = Field(..., description="Opaque activity identifier")
    title: str = Field(..., description="Buyer-readable activity label")
    status: str = Field(..., description="Current activity status")
    occurred_at: datetime = Field(..., description="When the activity occurred")
    project: ProjectRef | None = Field(None, description="Owning project")

    model_config = ConfigDict(from_attributes=True)


class DashboardBundleChangeSummary(BaseModel):
    """Minimal bundle change card for the dashboard."""

    pointer_id: UUID = Field(..., description="Backing pointer ID")
    bundle_name: str = Field(..., description="Buyer-facing bundle name")
    manifest_sha256: str | None = Field(None, description="Current manifest reference")
    changed_at: datetime = Field(..., description="When the bundle changed")
    project: ProjectRef | None = Field(None, description="Owning project")

    model_config = ConfigDict(from_attributes=True)


class DashboardResearchPackSummary(BaseModel):
    """Minimal research pack card for the dashboard."""

    id: str = Field(..., description="Research pack identifier")
    name: str = Field(..., description="Buyer-facing research pack name")
    updated_at: datetime = Field(..., description="When the pack changed")
    project: ProjectRef | None = Field(None, description="Owning project")

    model_config = ConfigDict(from_attributes=True)


class DashboardAttentionItem(BaseModel):
    """Anything the operator should notice immediately."""

    id: str = Field(..., description="Opaque attention item identifier")
    item_type: str = Field(..., description="Thin type label such as decision, project, or run")
    title: str = Field(..., description="Buyer-readable attention title")
    reason: str = Field(..., description="Why the item needs attention")
    severity: DashboardAttentionSeverity = Field(..., description="Attention severity")
    occurred_at: datetime = Field(..., description="When the issue surfaced")
    project: ProjectRef | None = Field(None, description="Owning project")

    model_config = ConfigDict(from_attributes=True)


class DashboardSummaryResponse(BaseModel):
    """Derived dashboard summary used by the buyer-facing overview page."""

    generated_at: datetime = Field(..., description="When the summary was generated")
    counts: DashboardCounts = Field(..., description="Top-line dashboard counts")
    active_runs: list[DashboardRunSummary] = Field(
        default_factory=list, description="Runs in flight"
    )
    workflow_activity: list[DashboardActivitySummary] = Field(
        default_factory=list,
        description="Recent workflow activity",
    )
    recent_bundle_changes: list[DashboardBundleChangeSummary] = Field(
        default_factory=list,
        description="Recent bundle changes",
    )
    recent_research_packs: list[DashboardResearchPackSummary] = Field(
        default_factory=list,
        description="Recent research packs",
    )
    key_projects: list[ProjectResponse] = Field(
        default_factory=list,
        description="Priority thin projects for the dashboard",
    )
    recent_decisions: list[DecisionResponse] = Field(
        default_factory=list,
        description="Most recent buyer-facing decisions",
    )
    attention_items: list[DashboardAttentionItem] = Field(
        default_factory=list,
        description="Anything that needs attention",
    )

    model_config = ConfigDict(from_attributes=True)
