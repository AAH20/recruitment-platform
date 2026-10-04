"""
Error handling middleware tests for recruitment-platform.

Tests that the error handling middleware correctly:
- Catches unhandled exceptions and returns 500
- Formats validation errors as 422 with detailed messages
- Formats HTTP exceptions with correct status codes
- Handles not-found (404) responses
- Handles method-not-allowed (405) responses
- Preserves error response structure (detail field)
- Logs errors appropriately
- Handles concurrent error scenarios
"""

import pytest
import logging
from unittest.mock import patch, MagicMock

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware


# ---------------------------------------------------------------------------
# Error handling middleware
# ---------------------------------------------------------------------------

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware that catches unhandled exceptions and formats them."""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
return response
except HTTPException:
            raise
except RequestValidationError as exc:
            return JSONResponse(
status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
content={
"detail": "Validation error",
"errors": exc.errors(),
},
)
        except Exception as exc:
            # Log the error
            logging.getLogger("error_handler").error(
f"Unhandled exception: {exc}", exc_info=True
)
            return JSONResponse(
status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
content={"detail": "Internal server error"},
)


# ---------------------------------------------------------------------------
# Pydantic models for validation testing
# ---------------------------------------------------------------------------

class JobCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
description: str = Field(..., min_length=10)
salary_min: int = Field(..., gt=0)
salary_max: int = Field(..., gt=0)
location: str = Field(..., min_length=2)


class CandidateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
experience_years: int = Field(..., ge=0, le=50)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app() -> FastAPI:
    """Create a FastAPI app with error handling middleware."""
app = FastAPI(title="Recruitment Platform — Error Handler Test App")
app.add_middleware(ErrorHandlerMiddleware)

    @app.get("/api/jobs")
async def list_jobs():
        return {"jobs": [{"id": 1, "title": "Engineer"}]}

    @app.get("/api/jobs/{job_id}")
async def get_job(job_id: int):
        if job_id == 999:
            raise HTTPException(
status_code=status.HTTP_404_NOT_FOUND,
detail="Job not found",
)
        return {"job_id": job_id, "title": "Engineer"}

    @app.post("/api/jobs", status_code=status.HTTP_201_CREATED)
async def create_job(job: JobCreate):
        return {"created": True, "title": job.title}

    @app.post("/api/candidates", status_code=status.HTTP_201_CREATED)
async def create_candidate(candidate: CandidateCreate):
        return {"created": True, "name": candidate.name}

    @app.get("/api/error/500")
async def trigger_server_error():
        raise RuntimeError("Something went wrong in the database")

    @app.get("/api/error/divide-by-zero")
async def trigger_divide_by_zero():
        result = 1 / 0
return {"result": result}

    @app.get("/api/error/key-error")
async def trigger_key_error():
        data = {}
return {"value": data["nonexistent_key"]}

    @app.get("/api/error/value-error")
async def trigger_value_error():
        raise ValueError("Invalid value provided")

    @app.get("/api/error/custom-http")
async def trigger_custom_http():
        raise HTTPException(
status_code=status.HTTP_403_FORBIDDEN,
detail="You don't have permission to access this resource",
)

    @app.get("/api/error/401")
async def trigger_unauthorized():
        raise HTTPException(
status_code=status.HTTP_401_UNAUTHORIZED,
detail="Authentication required",
)

    @app.get("/api/error/409")
async def trigger_conflict():
        raise HTTPException(
status_code=status.HTTP_409_CONFLICT,
detail="Resource already exists",
)

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Return a TestClient for the test app."""
return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Tests — HTTP exceptions
# ---------------------------------------------------------------------------

class TestHTTPExceptions:
    """HTTP exceptions should be formatted correctly."""

    def test_404_not_found(self, client: TestClient):
        response = client.get("/api/jobs/999")
assert response.status_code == 404
assert response.json()["detail"] == "Job not found"

    def test_403_forbidden(self, client: TestClient):
        response = client.get("/api/error/custom-http")
assert response.status_code == 403
assert "permission" in response.json()["detail"].lower()

    def test_401_unauthorized(self, client: TestClient):
        response = client.get("/api/error/401")
assert response.status_code == 401
assert "authentication" in response.json()["detail"].lower()

    def test_409_conflict(self, client: TestClient):
        response = client.get("/api/error/409")
assert response.status_code == 409
assert "already exists" in response.json()["detail"].lower()

    def test_404_on_nonexistent_route(self, client: TestClient):
        response = client.get("/api/nonexistent-route")
assert response.status_code == 404

    def test_405_method_not_allowed(self, client: TestClient):
        response = client.delete("/api/jobs")
assert response.status_code == 405


# ---------------------------------------------------------------------------
# Tests — validation errors (422)
# ---------------------------------------------------------------------------

class TestValidationErrors:
    """Validation errors should return 422 with detailed error info."""

    def test_missing_required_field(self, client: TestClient):
        response = client.post("/api/jobs", json={})
assert response.status_code == 422
body = response.json()
assert "detail" in body
assert "errors" in body
error_fields = [e["loc"][-1] for e in body["errors"]]
assert "title" in error_fields
assert "description" in error_fields

    def test_field_too_short(self, client: TestClient):
        response = client.post("/api/jobs", json={
"title": "AB",  # min_length is 3
"description": "Short desc",
"salary_min": 50000,
"salary_max": 100000,
"location": "Cairo",
})
assert response.status_code == 422
body = response.json()
error_fields = [e["loc"][-1] for e in body["errors"]]
assert "title" in error_fields

    def test_invalid_email_format(self, client: TestClient):
        response = client.post("/api/candidates", json={
"name": "Ahmed Hassan",
"email": "not-an-email",
"experience_years": 5,
})
assert response.status_code == 422
body = response.json()
error_fields = [e["loc"][-1] for e in body["errors"]]
assert "email" in error_fields

    def test_negative_salary(self, client: TestClient):
        response = client.post("/api/jobs", json={
"title": "Software Engineer",
"description": "A great job opportunity",
"salary_min": -1000,
"salary_max": 100000,
"location": "Cairo",
})
assert response.status_code == 422
body = response.json()
error_fields = [e["loc"][-1] for e in body["errors"]]
assert "salary_min" in error_fields

    def test_experience_years_out_of_range(self, client: TestClient):
        response = client.post("/api/candidates", json={
"name": "Ahmed",
"email": "ahmed@example.com",
"experience_years": 100,  # max is 50
})
assert response.status_code == 422
body = response.json()
error_fields = [e["loc"][-1] for e in body["errors"]]
assert "experience_years" in error_fields

    def test_valid_job_creation(self, client: TestClient):
        response = client.post("/api/jobs", json={
"title": "Senior Software Engineer",
"description": "Looking for an experienced engineer to join our team",
"salary_min": 50000,
"salary_max": 100000,
"location": "Cairo, Egypt",
})
assert response.status_code == 201
assert response.json()["created"] is True

    def test_valid_candidate_creation(self, client: TestClient):
        response = client.post("/api/candidates", json={
"name": "Ahmed Hassan",
"email": "ahmed.hassan@example.com",
"experience_years": 5,
})
assert response.status_code == 201
assert response.json()["created"] is True

    def test_validation_error_includes_location(self, client: TestClient):
        """Validation errors should include the field location."""
response = client.post("/api/jobs", json={
"title": "AB",
"description": "Short",
"salary_min": -1,
"salary_max": -2,
"location": "X",
})
assert response.status_code == 422
body = response.json()
for error in body["errors"]:
            assert "loc" in error
assert "msg" in error
assert "type" in error


# ---------------------------------------------------------------------------
# Tests — unhandled exceptions (500)
# ---------------------------------------------------------------------------

class TestUnhandledExceptions:
    """Unhandled exceptions should return 500 with generic message."""

    def test_runtime_error_returns_500(self, client: TestClient):
        response = client.get("/api/error/500")
assert response.status_code == 500
assert response.json()["detail"] == "Internal server error"

    def test_divide_by_zero_returns_500(self, client: TestClient):
        response = client.get("/api/error/divide-by-zero")
assert response.status_code == 500
assert response.json()["detail"] == "Internal server error"

    def test_key_error_returns_500(self, client: TestClient):
        response = client.get("/api/error/key-error")
assert response.status_code == 500
assert response.json()["detail"] == "Internal server error"

    def test_value_error_returns_500(self, client: TestClient):
        response = client.get("/api/error/value-error")
assert response.status_code == 500
assert response.json()["detail"] == "Internal server error"

    def test_500_response_is_json(self, client: TestClient):
        response = client.get("/api/error/500")
assert "application/json" in response.headers.get("content-type", "")

    def test_500_does_not_leak_internal_details(self, client: TestClient):
        """500 responses should not expose internal error details."""
response = client.get("/api/error/500")
body = response.json()
# Should only have "detail" key, not the actual exception message
        assert "detail" in body
assert "RuntimeError" not in str(body)
assert "Something went wrong" not in str(body)


# ---------------------------------------------------------------------------
# Tests — error response structure
# ---------------------------------------------------------------------------

class TestErrorResponseStructure:
    """All error responses should follow a consistent structure."""

    def test_error_response_has_detail_field(self, client: TestClient):
        """All error responses must have a 'detail' field."""
# 404
        response = client.get("/api/jobs/999")
assert "detail" in response.json()

        # 422
        response = client.post("/api/jobs", json={})
assert "detail" in response.json()

        # 500
        response = client.get("/api/error/500")
assert "detail" in response.json()

    def test_error_response_content_type(self, client: TestClient):
        """All error responses should be JSON."""
endpoints = [
("/api/jobs/999", "GET"),
            ("/api/error/500", "GET"),
            ("/api/nonexistent", "GET"),
        ]
for path, method in endpoints:
            response = client.request(method, path)
assert "application/json" in response.headers.get("content-type", ""), \
f"{method} {path} should return JSON"

    def test_successful_response_not_affected(self, client: TestClient):
        """Successful responses should not be modified by error middleware."""
response = client.get("/api/jobs")
assert response.status_code == 200
assert "jobs" in response.json()


# ---------------------------------------------------------------------------
# Tests — error logging
# ---------------------------------------------------------------------------

class TestErrorLogging:
    """Errors should be logged for debugging."""

    def test_unhandled_exception_is_logged(self, client: TestClient, caplog):
        """Unhandled exceptions should produce log entries."""
with caplog.at_level(logging.ERROR, logger="error_handler"):
            client.get("/api/error/500")
assert any("Unhandled exception" in record.message for record in caplog.records)

    def test_validation_error_not_logged_as_error(self, client: TestClient, caplog):
        """Validation errors are client errors, not server errors."""
with caplog.at_level(logging.ERROR, logger="error_handler"):
            client.post("/api/jobs", json={})
# Validation errors should not appear in error logs
        assert not any("Unhandled exception" in record.message for record in caplog.records)


# ---------------------------------------------------------------------------
# Tests — concurrent/multiple errors
# ---------------------------------------------------------------------------

class TestMultipleErrors:
    """Multiple sequential errors should all be handled correctly."""

    def test_multiple_500_errors(self, client: TestClient):
        """Multiple 500 errors should all return proper responses."""
for _ in range(3):
            response = client.get("/api/error/500")
assert response.status_code == 500
assert response.json()["detail"] == "Internal server error"

    def test_mixed_error_types(self, client: TestClient):
        """Different error types should be handled independently."""
# 404
        response = client.get("/api/jobs/999")
assert response.status_code == 404

        # 500
        response = client.get("/api/error/500")
assert response.status_code == 500

        # 422
        response = client.post("/api/jobs", json={})
assert response.status_code == 422

        # 200
        response = client.get("/api/jobs")
assert response.status_code == 200

    def test_error_recovery(self, client: TestClient):
        """After an error, the app should continue serving requests."""
# Trigger error
        response = client.get("/api/error/500")
assert response.status_code == 500

        # App should still work
        response = client.get("/api/jobs")
assert response.status_code == 200
assert "jobs" in response.json()
