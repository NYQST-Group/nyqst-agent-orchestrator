"""Background job queue using ARQ (Redis-based).

Provides async job scheduling for long-running tasks like:
- Document parsing
- Embedding generation
- Batch processing
- Cleanup tasks
"""

from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from intelli.config import settings
from intelli.core.logging import get_logger

logger = get_logger(__name__)

# Job registry
_job_registry: dict[str, Callable] = {}


def job(name: str | None = None):
    """Decorator to register a function as a background job.

    Usage:
        @job("parse_document")
        async def parse_document(ctx, artifact_sha: str):
            # Long-running work
            pass
    """
    def decorator(func: Callable) -> Callable:
        job_name = name or func.__name__
        _job_registry[job_name] = func
        return func
    return decorator


class JobQueue:
    """Interface for enqueueing background jobs.

    Falls back to synchronous execution if Redis unavailable.
    """

    def __init__(self):
        self._redis_pool = None

    async def _get_pool(self):
        """Get or create Redis connection pool."""
        if self._redis_pool is not None:
            return self._redis_pool

        if not settings.redis_url:
            return None

        try:
            from arq.connections import RedisSettings, create_pool

            # Parse Redis URL
            redis_settings = RedisSettings.from_dsn(settings.redis_url)
            self._redis_pool = await create_pool(redis_settings)
            return self._redis_pool
        except ImportError:
            logger.warning("arq not installed, jobs will run synchronously")
            return None
        except Exception as e:
            logger.warning("redis_unavailable", error=str(e))
            return None

    async def enqueue(
        self,
        job_name: str,
        *args,
        _job_id: str | None = None,
        _defer_by: timedelta | None = None,
        _defer_until: datetime | None = None,
        **kwargs,
    ) -> str:
        """Enqueue a job for background execution.

        Args:
            job_name: Name of the registered job
            *args: Positional arguments for the job
            _job_id: Optional custom job ID
            _defer_by: Delay execution by this duration
            _defer_until: Execute at this specific time
            **kwargs: Keyword arguments for the job

        Returns:
            Job ID
        """
        job_id = _job_id or str(uuid4())

        pool = await self._get_pool()
        if pool is None:
            # Fall back to synchronous execution
            logger.info("executing_job_sync", job_name=job_name, job_id=job_id)
            if job_name in _job_registry:
                try:
                    await _job_registry[job_name](None, *args, **kwargs)
                except Exception:
                    logger.exception("job_failed", job_name=job_name, job_id=job_id)
                    raise
            return job_id

        # Enqueue via ARQ
        try:

            await pool.enqueue_job(
                job_name,
                *args,
                _job_id=job_id,
                _defer_by=_defer_by,
                _defer_until=_defer_until,
                **kwargs,
            )
            logger.info("job_enqueued", job_name=job_name, job_id=job_id)
            return job_id

        except Exception as e:
            logger.warning("enqueue_failed", job_name=job_name, error=str(e))
            # Fall back to sync
            if job_name in _job_registry:
                await _job_registry[job_name](None, *args, **kwargs)
            return job_id

    async def get_job_result(self, job_id: str) -> Any | None:
        """Get result of a completed job."""
        pool = await self._get_pool()
        if pool is None:
            return None

        try:
            from arq.jobs import Job
            job = Job(job_id, pool)
            return await job.result(timeout=0)
        except Exception:
            return None

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job."""
        pool = await self._get_pool()
        if pool is None:
            return False

        try:
            from arq.jobs import Job
            job = Job(job_id, pool)
            await job.abort()
            return True
        except Exception:
            return False


# Global job queue instance
job_queue = JobQueue()


# Worker settings for ARQ (used by: arq intelli.core.jobs.WorkerSettings)
class WorkerSettings:
    """ARQ worker settings."""

    functions = list(_job_registry.values())

    @staticmethod
    def redis_settings():
        if not settings.redis_url:
            return None
        from arq.connections import RedisSettings
        return RedisSettings.from_dsn(settings.redis_url)

    # Worker configuration
    max_jobs = 10
    job_timeout = 3600  # 1 hour
    keep_result = 3600  # Keep results for 1 hour
    retry_jobs = True
    max_tries = 3


# ============================================================================
# Pre-defined Jobs
# ============================================================================

@job("parse_document")
async def parse_document_job(ctx, artifact_sha: str, run_id: str):
    """Parse a document using Docling.

    This is a long-running job that should be run in background.
    """
    logger.info("parsing_document", artifact_sha=artifact_sha, run_id=run_id)
    # Implementation would go here
    # from intelli.services.docir import DocIRService
    # ...


@job("generate_embeddings")
async def generate_embeddings_job(ctx, artifact_sha: str, chunk_ids: list[str]):
    """Generate embeddings for document chunks."""
    logger.info("generating_embeddings", artifact_sha=artifact_sha, chunk_count=len(chunk_ids))
    # Implementation would go here


@job("cleanup_orphaned_artifacts")
async def cleanup_orphaned_artifacts_job(ctx, older_than_days: int = 30):
    """Clean up artifacts with zero references."""
    logger.info("cleanup_orphaned_artifacts", older_than_days=older_than_days)
    # Implementation would go here
