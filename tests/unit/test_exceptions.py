"""Unit tests for exception hierarchy — status codes, messages, to_dict."""

from __future__ import annotations

import pytest

from intelli.core.exceptions import (
    ArtifactNotFoundError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DatabaseError,
    DuplicateResourceError,
    ExternalServiceError,
    IntelliError,
    ManifestNotFoundError,
    NotFoundError,
    PointerNotFoundError,
    RateLimitError,
    RunNotFoundError,
    StorageError,
    ValidationError,
    VersionConflictError,
)

pytestmark = pytest.mark.unit


class TestIntelliError:
    def test_default_values(self):
        err = IntelliError()
        assert err.status_code == 500
        assert err.code == "INTERNAL_ERROR"
        assert err.details == {}

    def test_custom_message(self):
        err = IntelliError(message="boom")
        assert str(err) == "boom"
        assert err.message == "boom"

    def test_to_dict(self):
        err = IntelliError(message="oops", code="MY_CODE")
        d = err.to_dict()
        assert d["error"]["code"] == "MY_CODE"
        assert d["error"]["message"] == "oops"


class TestClientErrors:
    def test_validation_error(self):
        err = ValidationError(message="bad input", field="email")
        assert err.status_code == 400
        assert err.details["field"] == "email"

    def test_authentication_error(self):
        err = AuthenticationError()
        assert err.status_code == 401
        assert err.code == "AUTHENTICATION_ERROR"

    def test_authorization_error(self):
        err = AuthorizationError()
        assert err.status_code == 403

    def test_not_found_error(self):
        err = NotFoundError(resource_type="Widget", identifier="42")
        assert err.status_code == 404
        assert "Widget" in err.message

    def test_conflict_error(self):
        err = ConflictError()
        assert err.status_code == 409

    def test_rate_limit_error(self):
        err = RateLimitError(limit=100, reset_after=30)
        assert err.status_code == 429
        assert err.details["limit"] == 100
        assert err.details["reset_after_seconds"] == 30


class TestResourceErrors:
    def test_artifact_not_found(self):
        sha = "a" * 64
        err = ArtifactNotFoundError(sha256=sha)
        assert err.code == "ARTIFACT_NOT_FOUND"
        assert err.details["sha256"] == sha

    def test_manifest_not_found(self):
        err = ManifestNotFoundError(sha256="b" * 64)
        assert err.code == "MANIFEST_NOT_FOUND"

    def test_pointer_not_found_by_namespace(self):
        err = PointerNotFoundError(namespace="ns", name="doc")
        assert "ns/doc" in err.message

    def test_run_not_found(self):
        err = RunNotFoundError(run_id="run-123")
        assert err.code == "RUN_NOT_FOUND"
        assert err.details["run_id"] == "run-123"

    def test_version_conflict(self):
        err = VersionConflictError(expected=3, actual=5)
        assert err.status_code == 409
        assert "3" in err.message and "5" in err.message

    def test_duplicate_resource(self):
        err = DuplicateResourceError()
        assert err.code == "DUPLICATE_RESOURCE"


class TestServerErrors:
    def test_storage_error(self):
        err = StorageError(operation="put")
        assert err.status_code == 500
        assert err.details["operation"] == "put"

    def test_database_error(self):
        err = DatabaseError()
        assert err.status_code == 500

    def test_external_service_error(self):
        err = ExternalServiceError()
        assert err.status_code == 502
