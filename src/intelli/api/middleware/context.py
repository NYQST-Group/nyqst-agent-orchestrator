"""Auth context middleware.

Resolves authentication from request headers and sets request.state.context
for all downstream handlers. This is the extension point for future context
resolution (hierarchy walking, config snapshots, insight injection per the
Knowledge & Context design doc §3.3).

Currently handles:
- Bearer token → RequestContext with tenant_id, user_id, role, scopes
- API key → RequestContext with tenant_id, scopes

Future (Phase 3):
- Scope resolution from request body/path (scope_type, scope_id)
- Config inheritance chain walk
- Insight injection into resolved config
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from intelli.api.middleware.auth import get_api_key_auth, get_bearer_auth
from intelli.core.context import set_context
from intelli.db.engine import get_session_factory


class AuthContextMiddleware(BaseHTTPMiddleware):
    """Populate request.state.context with auth info for all requests.

    Non-blocking: if no valid auth is present, request.state.context is None
    and the request proceeds. Individual endpoints can enforce auth via
    AuthContext / OptionalAuthContext dependencies as needed.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        context = None

        # Extract credentials from headers
        api_key = request.headers.get("x-api-key")
        auth_header = request.headers.get("authorization", "")
        bearer_token = None
        if auth_header.lower().startswith("bearer "):
            bearer_token = auth_header[7:].strip()

        # Only hit the DB if we have credentials to check
        if api_key or bearer_token:
            async with get_session_factory()() as session:
                try:
                    if api_key:
                        context = await get_api_key_auth(session, api_key, request)
                    if not context and bearer_token:
                        context = await get_bearer_auth(session, bearer_token, request)
                    await session.commit()
                except Exception:
                    await session.rollback()
                    # Auth failure is non-fatal for this middleware
                    context = None

        request.state.context = context
        if context:
            set_context(context)

        return await call_next(request)
