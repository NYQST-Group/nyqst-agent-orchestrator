"""Security utilities and authentication.

Provides:
- Password hashing (argon2)
- JWT token generation/validation
- API key validation
- Rate limiting
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

from intelli.config import settings

# Password hashing with Argon2 (recommended for new applications)
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_api_key(key: str) -> str:
    """Hash an API key using SHA-256."""
    return hashlib.sha256(key.encode()).hexdigest()


def generate_api_key() -> tuple[str, str, str]:
    """Generate a new API key.

    Returns:
        Tuple of (full_key, prefix, hash)
    """
    random_part = secrets.token_hex(16)
    full_key = f"int_{random_part}"
    prefix = full_key[:12]
    key_hash = hash_api_key(full_key)
    return full_key, prefix, key_hash


# JWT Configuration
JWT_SECRET = settings.secret_key
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24


def create_access_token(
    subject: str,
    tenant_id: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token.

    Args:
        subject: User ID or identifier
        tenant_id: Tenant ID for isolation
        role: User role for authorization
        expires_delta: Custom expiry time
    """
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(hours=JWT_EXPIRY_HOURS)
    )

    payload = {
        "sub": subject,
        "tid": tenant_id,  # Tenant ID
        "role": role,
        "exp": expire,
        "iat": datetime.now(UTC),
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Decode and validate a JWT access token.

    Returns:
        Decoded payload or None if invalid/expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


class RateLimiter:
    """Simple in-memory rate limiter.

    For production, use Redis-based rate limiting.
    This is a placeholder that demonstrates the interface.
    """

    def __init__(self):
        self._requests: dict[str, list[datetime]] = {}

    def is_allowed(self, key: str, limit: int, window_seconds: int = 60) -> bool:
        """Check if request is allowed under rate limit.

        Args:
            key: Unique identifier (API key ID, IP, etc.)
            limit: Max requests per window
            window_seconds: Time window in seconds

        Returns:
            True if request is allowed
        """
        now = datetime.now(UTC)
        window_start = now - timedelta(seconds=window_seconds)

        # Get existing requests for this key
        if key not in self._requests:
            self._requests[key] = []

        # Filter to only requests within window
        self._requests[key] = [
            ts for ts in self._requests[key] if ts > window_start
        ]

        # Check if under limit
        if len(self._requests[key]) >= limit:
            return False

        # Record this request
        self._requests[key].append(now)
        return True

    def get_remaining(self, key: str, limit: int, window_seconds: int = 60) -> int:
        """Get remaining requests in current window."""
        now = datetime.now(UTC)
        window_start = now - timedelta(seconds=window_seconds)

        if key not in self._requests:
            return limit

        recent = [ts for ts in self._requests[key] if ts > window_start]
        return max(0, limit - len(recent))


# Global rate limiter instance
rate_limiter = RateLimiter()
