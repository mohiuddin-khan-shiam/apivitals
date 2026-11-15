"""Pydantic data models for ApiVitals catalog, specifications, and health metrics."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator

StatusState = Literal["healthy", "degraded", "offline", "unknown"]
AuthType = Literal["none", "api_key", "oauth2"]


class ApiEndpoint(BaseModel):
    """Specification for a monitored API endpoint."""

    name: str = Field(..., description="Human-friendly name for this endpoint")
    path: str = Field(..., description="Full URL or probe path for testing")
    method: Literal["GET", "HEAD"] = Field(default="GET", description="HTTP probe method")
    expected_status: int = Field(default=200, description="Expected HTTP response status code")
    expected_content_type: str | None = Field(
        default=None, description="Expected substring in Content-Type header (e.g. 'json')"
    )
    headers: dict[str, str] = Field(default_factory=dict, description="Headers to include in probe")

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError(f"Endpoint path must start with http:// or https://: {v}")
        return v


class ApiDefinition(BaseModel):
    """Declarative metadata for a curated public API."""

    id: str = Field(..., description="Unique kebab-case slug (e.g., 'open-meteo')")
    name: str = Field(..., description="Display title of the API")
    description: str = Field(..., description="Concise summary of functionality")
    category: str = Field(..., description="Category group (e.g. 'Weather & Climate')")
    homepage: str = Field(..., description="Project website or organization URL")
    documentation: str = Field(..., description="Official documentation URL")
    auth: AuthType = Field(default="none", description="Authentication requirement")
    https: bool = Field(default=True, description="Whether endpoint supports HTTPS")
    cors: bool = Field(default=True, description="Whether endpoint allows cross-origin requests")
    endpoints: list[ApiEndpoint] = Field(..., min_length=1, description="List of probe endpoints")
    tags: list[str] = Field(default_factory=list, description="Search and classification tags")
    license: str = Field(default="Open / Unknown", description="Upstream data or code license")
    rate_limit: str = Field(default="Unspecified", description="Documented public rate limits")

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not v.replace("-", "").isalnum() or not v.islower():
            raise ValueError(f"ID must be lowercase alphanumeric with hyphens: '{v}'")
        return v


class HealthProbeResult(BaseModel):
    """Raw measurement from a single endpoint probe execution."""

    api_id: str
    endpoint_name: str
    url: str
    status_code: int | None = None
    latency_ms: float = 0.0
    is_healthy: bool = False
    cors_detected: bool = False
    ssl_valid: bool = False
    ssl_days_remaining: int | None = None
    error_message: str | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DailyHealthRecord(BaseModel):
    """Daily aggregated health check record for historical trends."""

    date: str = Field(..., description="Date formatted as YYYY-MM-DD")
    is_healthy: bool
    latency_ms: float
    status_code: int | None = None


class ServiceStatus(BaseModel):
    """Current health state, latency benchmarks, and uptime metrics for an API."""

    api_id: str
    name: str
    category: str
    state: StatusState
    latency_ms: float
    status_code: int | None
    cors_supported: bool
    ssl_days_remaining: int | None = None
    last_checked: str
    uptime_7d_percent: float = 100.0
    uptime_30d_percent: float = 100.0
    current_streak_days: int = 1
    error_detail: str | None = None


class ApiCatalog(BaseModel):
    """Exported complete catalog of public APIs with current vitals."""

    version: str = "1.0.0"
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_apis: int
    categories: list[str]
    apis: list[ApiDefinition]


class NetworkVitalsSummary(BaseModel):
    """Global snapshot summary of all monitored APIs."""

    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_monitored: int
    healthy_count: int
    degraded_count: int
    offline_count: int
    overall_uptime_pct: float
    avg_latency_ms: float
    p95_latency_ms: float
    services: list[ServiceStatus]
