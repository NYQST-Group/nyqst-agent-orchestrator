"""API v1 endpoints."""

from fastapi import APIRouter

from intelli.api.v1.artifacts import router as artifacts_router
from intelli.api.v1.auth import router as auth_router
from intelli.api.v1.health import router as health_router
from intelli.api.v1.manifests import router as manifests_router
from intelli.api.v1.pointers import router as pointers_router
from intelli.api.v1.rag import router as rag_router
from intelli.api.v1.runs import router as runs_router
from intelli.api.v1.streams import router as streams_router

router = APIRouter(prefix="/api/v1")

router.include_router(health_router)
router.include_router(auth_router)
router.include_router(artifacts_router)
router.include_router(manifests_router)
router.include_router(pointers_router)
router.include_router(rag_router)
router.include_router(runs_router)
router.include_router(streams_router)
