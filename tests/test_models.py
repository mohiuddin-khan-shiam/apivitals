"""Unit tests for Pydantic data schemas in apivitals.models."""

import pytest
from pydantic import ValidationError

from apivitals.models import (
    ApiDefinition,
    ApiEndpoint,
    NetworkVitalsSummary,
    ServiceStatus,
)


def test_valid_api_definition() -> None:
    api = ApiDefinition(
        id="sample-api",
        name="Sample API",
        description="A test API for unit tests.",
        category="Developer Tools",
        homepage="https://example.com",
        documentation="https://example.com/docs",
        auth="none",
        https=True,
        cors=True,
        endpoints=[
            ApiEndpoint(
                name="Ping",
                path="https://example.com/ping",
                method="GET",
                expected_status=200,
            )
        ],
        tags=["test", "sample"],
        license="MIT",
        rate_limit="100/min",
    )
    assert api.id == "sample-api"
    assert len(api.endpoints) == 1
    assert api.endpoints[0].method == "GET"


def test_invalid_api_id_uppercase() -> None:
    with pytest.raises(ValidationError):
        ApiDefinition(
            id="Invalid_ID",
            name="Sample",
            description="Test",
            category="Test",
            homepage="https://example.com",
            documentation="https://example.com/docs",
            endpoints=[ApiEndpoint(name="Test", path="https://example.com/test")],
        )


def test_invalid_endpoint_url() -> None:
    with pytest.raises(ValidationError):
        ApiEndpoint(name="Bad", path="ftp://example.com/file")


def test_service_status_model() -> None:
    status = ServiceStatus(
        api_id="sample-api",
        name="Sample API",
        category="Developer Tools",
        state="healthy",
        latency_ms=124.5,
        status_code=200,
        cors_supported=True,
        ssl_days_remaining=90,
        last_checked="2026-11-16T00:00:00Z",
        uptime_7d_percent=100.0,
        uptime_30d_percent=98.5,
        current_streak_days=14,
    )
    assert status.state == "healthy"
    assert status.latency_ms == 124.5
    assert status.current_streak_days == 14


def test_vitals_summary_model() -> None:
    summary = NetworkVitalsSummary(
        total_monitored=10,
        healthy_count=9,
        degraded_count=1,
        offline_count=0,
        overall_uptime_pct=100.0,
        avg_latency_ms=150.2,
        p95_latency_ms=320.0,
        services=[],
    )
    assert summary.healthy_count == 9
    assert summary.total_monitored == 10
