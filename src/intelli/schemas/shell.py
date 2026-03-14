"""Schemas for shell context and operator summary surfaces."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ShellContextEntity(BaseModel):
    """Lightweight entity shown in breadcrumbs and switchers."""

    id: str
    label: str
    href: str | None = None
    subtitle: str | None = None


class ShellModelOption(BaseModel):
    """Selectable model option exposed to the shell."""

    id: str
    label: str
    provider: str | None = None
    is_default: bool = False


class ShellSessionSummary(BaseModel):
    """Recent or active session summary."""

    id: UUID
    module: str | None = None
    objective: str | None = None
    status: str
    last_active_at: datetime
    started_at: datetime


class ShellContextResponse(BaseModel):
    """Top-bar context for the product shell."""

    workspace_name: str
    workspace_id: str
    initiative_name: str | None = None
    active_project: ShellContextEntity | None = None
    active_task: ShellContextEntity | None = None
    active_session: ShellSessionSummary | None = None
    current_user_role: str | None = None
    available_models: list[ShellModelOption] = Field(default_factory=list)
    recent_entities: list[ShellContextEntity] = Field(default_factory=list)


class OpsActivityItem(BaseModel):
    """Recent operational activity for the shell overlay."""

    id: str
    label: str
    detail: str
    href: str | None = None
    timestamp: datetime
    kind: str = "run"
    status: str | None = None


class UsageSummaryItem(BaseModel):
    """Token and cost summary for a model or scope."""

    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_micros: int = 0


class OpsSummaryResponse(BaseModel):
    """Counts and recent activity for the operations overlay."""

    active_runs: list[OpsActivityItem] = Field(default_factory=list)
    recent_activity: list[OpsActivityItem] = Field(default_factory=list)
    queued_count: int = 0
    running_count: int = 0
    failed_count: int = 0
    unread_operational_items: int = 0
    price_table_version: str | None = None
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost_micros: int = 0
    cost_by_model: list[UsageSummaryItem] = Field(default_factory=list)


class RightRailItem(BaseModel):
    """Single route-aware right-rail entry."""

    id: str
    title: str
    subtitle: str | None = None
    meta: str | None = None
    href: str | None = None
    badge: str | None = None


class RightRailSection(BaseModel):
    """Product-shell right-rail section."""

    kind: str
    title: str
    description: str | None = None
    items: list[RightRailItem] = Field(default_factory=list)


class RightRailResponse(BaseModel):
    """Route-aware right-rail payload."""

    module: str
    sections: list[RightRailSection] = Field(default_factory=list)
