"""Shell context and operator summary endpoints."""

from collections.abc import Iterable
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from intelli.api.dependencies import get_session
from intelli.api.middleware.auth import AuthContext
from intelli.config import settings
from intelli.db.models.auth import Tenant
from intelli.db.models.conversations import Session as SessionModel
from intelli.db.models.runs import Run
from intelli.db.models.substrate import Pointer
from intelli.schemas.shell import (
    OpsActivityItem,
    OpsSummaryResponse,
    RightRailItem,
    RightRailResponse,
    RightRailSection,
    ShellContextEntity,
    ShellContextResponse,
    ShellModelOption,
    ShellSessionSummary,
    UsageSummaryItem,
)
from intelli.services.usage.pricing import PRICE_TABLE_VERSION, format_cost_usd

router = APIRouter(tags=["shell"])

SHELL_MODULES = {"overview", "research", "docs", "analysis", "projects", "clients", "decisions"}


def _titleize_module(module: str | None) -> str:
    if not module:
        return "Workspace"
    return module.replace("_", " ").replace("-", " ").title()


def _coerce_entity(raw: Any, default_href: str | None = None) -> ShellContextEntity | None:
    if raw is None:
        return None

    if isinstance(raw, str):
        label = raw.strip()
        if not label:
            return None
        return ShellContextEntity(id=label.lower().replace(" ", "-"), label=label, href=default_href)

    if isinstance(raw, dict):
        label = raw.get("label") or raw.get("name") or raw.get("title")
        if not isinstance(label, str) or not label.strip():
            return None
        entity_id = raw.get("id") or raw.get("slug") or label.lower().replace(" ", "-")
        subtitle = raw.get("subtitle") or raw.get("description")
        href = raw.get("href") or default_href
        return ShellContextEntity(
            id=str(entity_id),
            label=label.strip(),
            href=href if isinstance(href, str) else default_href,
            subtitle=subtitle if isinstance(subtitle, str) else None,
        )

    return None


def _extract_workspace_context(session_obj: SessionModel | None) -> tuple[str | None, ShellContextEntity | None, ShellContextEntity | None]:
    if session_obj is None or not isinstance(session_obj.workspace, dict):
        return None, None, None

    workspace = session_obj.workspace
    initiative_name: str | None = None
    initiative = workspace.get("initiative")
    if isinstance(initiative, str) and initiative.strip():
        initiative_name = initiative.strip()
    elif isinstance(initiative, dict):
        initiative_name = (
            initiative.get("label")
            or initiative.get("name")
            or initiative.get("title")
        )
    else:
        initiative_name = workspace.get("initiative_name")
        if not isinstance(initiative_name, str):
            initiative_name = None

    return (
        initiative_name,
        _coerce_entity(workspace.get("project"), "/projects"),
        _coerce_entity(workspace.get("task"), "/projects"),
    )


def _build_run_activity(run: Run) -> OpsActivityItem:
    label = run.name or _titleize_module(run.run_type)
    detail = run.run_type.replace("_", " ")
    if run.project_id:
        detail = f"{detail} · linked project"
    href = "/research" if run.run_type in {"research", "document_parse", "rag_ask"} else "/overview"
    return OpsActivityItem(
        id=str(run.id),
        label=label,
        detail=detail,
        href=href,
        timestamp=run.created_at,
        kind="run",
        status=run.status,
    )


def _aggregate_run_usage(runs: Iterable[Run]) -> tuple[int, int, int, list[UsageSummaryItem]]:
    by_model: dict[str, dict[str, int]] = {}
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost_micros = 0

    for run in runs:
        if not isinstance(run.token_usage, dict):
            continue
        for model, usage in run.token_usage.items():
            if not isinstance(usage, dict):
                continue
            input_tokens = int(usage.get("input_tokens", usage.get("input", 0)) or 0)
            output_tokens = int(usage.get("output_tokens", usage.get("output", 0)) or 0)
            cost_micros = int(usage.get("cost_micros", 0) or 0)
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            total_cost_micros += cost_micros
            bucket = by_model.setdefault(
                model,
                {"input_tokens": 0, "output_tokens": 0, "cost_micros": 0},
            )
            bucket["input_tokens"] += input_tokens
            bucket["output_tokens"] += output_tokens
            bucket["cost_micros"] += cost_micros

    return (
        total_input_tokens,
        total_output_tokens,
        total_cost_micros,
        [
            UsageSummaryItem(
                model=model,
                input_tokens=totals["input_tokens"],
                output_tokens=totals["output_tokens"],
                cost_micros=totals["cost_micros"],
            )
            for model, totals in sorted(
                by_model.items(),
                key=lambda item: (-item[1]["cost_micros"], item[0]),
            )
        ],
    )


def _build_pointer_item(pointer: Pointer, module: str) -> RightRailItem:
    ready = "Ready" if pointer.manifest_sha256 else "Empty"
    href = f"/docs/{pointer.id}" if module in {"docs", "overview"} else "/docs"
    return RightRailItem(
        id=str(pointer.id),
        title=pointer.name,
        subtitle=pointer.description or f"{pointer.pointer_type.title()} source library",
        meta=f"{pointer.namespace} · updated {pointer.updated_at.strftime('%d %b %H:%M')}",
        href=href,
        badge=ready,
    )


def _recent_sessions_query(ctx: AuthContext) -> Select[tuple[SessionModel]]:
    stmt = select(SessionModel).where(SessionModel.tenant_id == ctx.tenant_id)
    if ctx.user_id:
        stmt = stmt.where(SessionModel.user_id == ctx.user_id)
    return stmt.order_by(SessionModel.last_active_at.desc()).limit(8)


async def _load_recent_sessions(db: AsyncSession, ctx: AuthContext) -> list[SessionModel]:
    result = await db.execute(_recent_sessions_query(ctx))
    return list(result.scalars())


async def _load_recent_runs(
    db: AsyncSession,
    session_ids: Iterable[Any],
    ctx: AuthContext,
) -> list[Run]:
    session_ids = [sid for sid in session_ids if sid]
    stmt = select(Run)
    if session_ids and ctx.user_id:
        stmt = stmt.where(or_(Run.session_id.in_(session_ids), Run.created_by == ctx.user_id))
    elif session_ids:
        stmt = stmt.where(Run.session_id.in_(session_ids))
    elif ctx.user_id:
        stmt = stmt.where(Run.created_by == ctx.user_id)
    else:
        stmt = stmt.order_by(Run.created_at.desc()).limit(0)

    stmt = stmt.order_by(Run.created_at.desc()).limit(20)
    result = await db.execute(stmt)
    return list(result.scalars())


async def _load_recent_pointers(db: AsyncSession) -> list[Pointer]:
    result = await db.execute(
        select(Pointer)
        .where(Pointer.deleted_at.is_(None))
        .order_by(Pointer.updated_at.desc())
        .limit(8)
    )
    return list(result.scalars())


@router.get("/shell/context", response_model=ShellContextResponse)
async def get_shell_context(
    ctx: AuthContext,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> ShellContextResponse:
    tenant = await db.scalar(select(Tenant).where(Tenant.id == ctx.tenant_id))
    recent_sessions = await _load_recent_sessions(db, ctx)
    active_session = next(
        (item for item in recent_sessions if item.status in {"active", "running", "paused", "idle"}),
        recent_sessions[0] if recent_sessions else None,
    )
    initiative_name, active_project, active_task = _extract_workspace_context(active_session)

    recent_entities: list[ShellContextEntity] = []
    seen_ids: set[str] = set()
    for session_obj in recent_sessions[:4]:
        label = session_obj.objective or _titleize_module(session_obj.module)
        entity = ShellContextEntity(
            id=str(session_obj.id),
            label=label,
            subtitle=f"{_titleize_module(session_obj.module)} · {session_obj.status}",
            href="/research" if session_obj.module == "research" else "/overview",
        )
        if entity.id not in seen_ids:
            seen_ids.add(entity.id)
            recent_entities.append(entity)

    for pointer in await _load_recent_pointers(db):
        if len(recent_entities) >= 6:
            break
        entity = ShellContextEntity(
            id=str(pointer.id),
            label=pointer.name,
            subtitle=f"{pointer.namespace} source library",
            href=f"/docs/{pointer.id}",
        )
        if entity.id not in seen_ids:
            seen_ids.add(entity.id)
            recent_entities.append(entity)

    return ShellContextResponse(
        workspace_name=tenant.name if tenant else "Workspace",
        workspace_id=str(ctx.tenant_id),
        initiative_name=initiative_name,
        active_project=active_project,
        active_task=active_task,
        active_session=(
            ShellSessionSummary(
                id=active_session.id,
                module=active_session.module,
                objective=active_session.objective,
                status=active_session.status,
                last_active_at=active_session.last_active_at,
                started_at=active_session.started_at,
            )
            if active_session
            else None
        ),
        current_user_role=ctx.role,
        available_models=[
            ShellModelOption(
                id=settings.chat_model,
                label=settings.chat_model,
                provider="OpenAI" if settings.chat_model.startswith("gpt") else None,
                is_default=True,
            )
        ],
        recent_entities=recent_entities,
    )


@router.get("/ops/summary", response_model=OpsSummaryResponse)
async def get_ops_summary(
    ctx: AuthContext,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> OpsSummaryResponse:
    recent_sessions = await _load_recent_sessions(db, ctx)
    recent_runs = await _load_recent_runs(db, [item.id for item in recent_sessions], ctx)
    running = [run for run in recent_runs if run.status in {"running", "paused"}]
    queued = [run for run in recent_runs if run.status == "pending"]
    failed = [run for run in recent_runs if run.status == "failed"]
    total_input_tokens, total_output_tokens, total_cost_micros, cost_by_model = _aggregate_run_usage(recent_runs)

    recent_activity = [_build_run_activity(run) for run in recent_runs[:8]]
    active_runs = [_build_run_activity(run) for run in running[:5]]

    return OpsSummaryResponse(
        active_runs=active_runs,
        recent_activity=recent_activity,
        queued_count=len(queued),
        running_count=len(running),
        failed_count=len(failed),
        unread_operational_items=len(failed) + len(queued),
        price_table_version=PRICE_TABLE_VERSION,
        total_input_tokens=total_input_tokens,
        total_output_tokens=total_output_tokens,
        total_cost_micros=total_cost_micros,
        cost_by_model=cost_by_model,
    )


@router.get("/shell/right-rail", response_model=RightRailResponse)
async def get_right_rail(
    ctx: AuthContext,
    db: Annotated[AsyncSession, Depends(get_session)],
    module: Annotated[str, Query(description="Current module name")] = "overview",
) -> RightRailResponse:
    normalized_module = module.strip().lower()
    if normalized_module not in SHELL_MODULES:
        normalized_module = "overview"

    recent_sessions = await _load_recent_sessions(db, ctx)
    recent_runs = await _load_recent_runs(db, [item.id for item in recent_sessions], ctx)
    recent_pointers = await _load_recent_pointers(db)
    usage_input_tokens, usage_output_tokens, usage_cost_micros, usage_by_model = _aggregate_run_usage(recent_runs)

    sections: list[RightRailSection] = []

    if normalized_module in {"overview", "projects", "clients", "decisions"}:
        plan_items = [
            RightRailItem(
                id=str(item.id),
                title=item.objective or f"{_titleize_module(item.module)} session",
                subtitle=f"{_titleize_module(item.module)} · {item.status}",
                meta=item.last_active_at.strftime("%d %b %H:%M"),
                href="/research" if item.module == "research" else "/overview",
            )
            for item in recent_sessions[:4]
        ]
        if plan_items:
            sections.append(
                RightRailSection(
                    kind="plans",
                    title="Current working sessions",
                    description="Recent sessions you can step back into from the shell.",
                    items=plan_items,
                )
            )

    if normalized_module in {"overview", "research", "docs"}:
        pointer_title = "Source libraries" if normalized_module != "research" else "Available sources"
        pointer_kind = "working_files" if normalized_module == "docs" else "sources"
        pointer_items = [_build_pointer_item(pointer, normalized_module) for pointer in recent_pointers[:5]]
        if pointer_items:
            sections.append(
                RightRailSection(
                    kind=pointer_kind,
                    title=pointer_title,
                    description="Versioned evidence bundles available in the current workspace.",
                    items=pointer_items,
                )
            )

    if normalized_module in {"overview", "research", "docs"} and (
        usage_input_tokens or usage_output_tokens or usage_cost_micros
    ):
        usage_items = [
            RightRailItem(
                id="usage-summary",
                title="Workspace testing usage",
                subtitle=f"{usage_input_tokens:,} input · {usage_output_tokens:,} output",
                meta=f"{format_cost_usd(usage_cost_micros)} · {PRICE_TABLE_VERSION}",
            )
        ]
        usage_items.extend(
            RightRailItem(
                id=f"usage-{item.model}",
                title=item.model,
                subtitle=f"{item.input_tokens:,} input · {item.output_tokens:,} output",
                meta=format_cost_usd(item.cost_micros),
            )
            for item in usage_by_model[:3]
        )
        sections.append(
            RightRailSection(
                kind="usage",
                title="Testing cost",
                description="Recent model usage and estimated spend from the internal meter.",
                items=usage_items,
            )
        )

    activity_items = [
        RightRailItem(
            id=str(run.id),
            title=run.name or _titleize_module(run.run_type),
            subtitle=f"{run.run_type.replace('_', ' ')} · {run.status}",
            meta=run.created_at.strftime("%d %b %H:%M"),
            href="/overview",
            badge=run.status.title(),
        )
        for run in recent_runs[:5]
    ]
    if activity_items:
        sections.append(
            RightRailSection(
                kind="activity",
                title="Recent activity",
                description="Live operational context from the shared run ledger.",
                items=activity_items,
            )
        )

    if not sections:
        sections.append(
            RightRailSection(
                kind="empty_state",
                title="No route context yet",
                description="This surface will become richer as sessions, sources, and runs accumulate.",
                items=[],
            )
        )

    return RightRailResponse(module=normalized_module, sections=sections)
