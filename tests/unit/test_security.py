"""Unit tests for core security module — JWT, password hashing, API keys."""

from __future__ import annotations

from datetime import timedelta

import jwt
import pytest

from intelli.core.security import (
    JWT_ALGORITHM,
    RateLimiter,
    create_access_token,
    decode_access_token,
    generate_api_key,
    hash_api_key,
    hash_password,
    verify_password,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Password hashing (Argon2)
# ---------------------------------------------------------------------------


class TestPasswordHashing:
    def test_hash_returns_argon2_string(self):
        hashed = hash_password("secret123")
        assert hashed.startswith("$argon2")

    def test_verify_correct_password(self):
        hashed = hash_password("myPassword!")
        assert verify_password("myPassword!", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("myPassword!")
        assert verify_password("wrongPassword", hashed) is False

    def test_different_passwords_produce_different_hashes(self):
        h1 = hash_password("password1")
        h2 = hash_password("password2")
        assert h1 != h2

    def test_same_password_produces_different_hashes_due_to_salt(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2


# ---------------------------------------------------------------------------
# JWT tokens
# ---------------------------------------------------------------------------


class TestJWT:
    def test_create_and_decode_roundtrip(self):
        token = create_access_token(
            subject="user-1",
            tenant_id="tenant-1",
            role="member",
        )
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user-1"
        assert payload["tid"] == "tenant-1"
        assert payload["role"] == "member"

    def test_token_contains_exp_and_iat(self):
        token = create_access_token("u", "t", "r")
        payload = decode_access_token(token)
        assert "exp" in payload
        assert "iat" in payload

    def test_custom_expiry(self):
        token = create_access_token("u", "t", "r", expires_delta=timedelta(minutes=5))
        payload = decode_access_token(token)
        assert payload is not None

    def test_expired_token_returns_none(self):
        token = create_access_token("u", "t", "r", expires_delta=timedelta(seconds=-1))
        assert decode_access_token(token) is None

    def test_invalid_token_returns_none(self):
        assert decode_access_token("not.a.token") is None

    def test_tampered_token_returns_none(self):
        token = create_access_token("u", "t", "r")
        tampered = token[:-4] + "XXXX"
        assert decode_access_token(tampered) is None

    def test_wrong_secret_returns_none(self):
        payload = {"sub": "u", "tid": "t", "role": "r", "exp": 9999999999}
        token = jwt.encode(payload, "wrong-secret", algorithm=JWT_ALGORITHM)
        assert decode_access_token(token) is None


# ---------------------------------------------------------------------------
# API key generation
# ---------------------------------------------------------------------------


class TestAPIKeyGeneration:
    def test_generate_returns_three_values(self):
        full_key, prefix, key_hash = generate_api_key()
        assert isinstance(full_key, str)
        assert isinstance(prefix, str)
        assert isinstance(key_hash, str)

    def test_key_starts_with_int_prefix(self):
        full_key, _, _ = generate_api_key()
        assert full_key.startswith("int_")

    def test_prefix_is_first_12_chars(self):
        full_key, prefix, _ = generate_api_key()
        assert prefix == full_key[:12]

    def test_hash_matches_key(self):
        full_key, _, key_hash = generate_api_key()
        assert hash_api_key(full_key) == key_hash


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------


class TestRateLimiter:
    def test_allows_within_limit(self):
        rl = RateLimiter()
        for _ in range(5):
            assert rl.is_allowed("k", limit=5) is True

    def test_blocks_over_limit(self):
        rl = RateLimiter()
        for _ in range(3):
            rl.is_allowed("k", limit=3)
        assert rl.is_allowed("k", limit=3) is False

    def test_get_remaining(self):
        rl = RateLimiter()
        assert rl.get_remaining("k", limit=10) == 10
        rl.is_allowed("k", limit=10)
        assert rl.get_remaining("k", limit=10) == 9

    def test_separate_keys_are_independent(self):
        rl = RateLimiter()
        for _ in range(3):
            rl.is_allowed("a", limit=3)
        assert rl.is_allowed("a", limit=3) is False
        assert rl.is_allowed("b", limit=3) is True
