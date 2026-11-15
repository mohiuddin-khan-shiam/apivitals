"""Unit tests for the probing engine and status evaluation."""

import httpx
import pytest

from apivitals.models import ApiDefinition, ApiEndpoint, HealthProbeResult
from apivitals.prober import (
    evaluate_service_status,
    probe_endpoint_async,
)


@pytest.fixture
def sample_api() -> ApiDefinition:
    return ApiDefinition(
        id="mock-service",
        name="Mock Service",
        description="A service for mocking responses.",
        category="Developer Tools",
        homepage="https://example.com",
        documentation="https://example.com/docs",
        endpoints=[
            ApiEndpoint(
                name="Ping",
                path="https://example.com/api/ping",
                expected_status=200,
                expected_content_type="json",
            )
        ],
    )


@pytest.mark.asyncio
async def test_probe_endpoint_mock_success(sample_api: ApiDefinition) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            json={"status": "ok"},
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        result = await probe_endpoint_async(sample_api.id, sample_api.endpoints[0], client)

    assert result.is_healthy is True
    assert result.status_code == 200
    assert result.cors_detected is True
    assert result.latency_ms >= 0


@pytest.mark.asyncio
async def test_probe_endpoint_mock_failure(sample_api: ApiDefinition) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "Internal Error"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        result = await probe_endpoint_async(sample_api.id, sample_api.endpoints[0], client)

    assert result.is_healthy is False
    assert result.status_code == 500
    assert result.error_message is not None


def test_evaluate_service_status_healthy(sample_api: ApiDefinition) -> None:
    results = [
        HealthProbeResult(
            api_id=sample_api.id,
            endpoint_name="Ping",
            url="https://example.com/api/ping",
            status_code=200,
            latency_ms=150.0,
            is_healthy=True,
            cors_detected=True,
            ssl_valid=True,
            ssl_days_remaining=90,
        )
    ]
    status = evaluate_service_status(sample_api, results)
    assert status.state == "healthy"
    assert status.latency_ms == 150.0
    assert status.cors_supported is True
    assert status.current_streak_days == 1


def test_evaluate_service_status_degraded(sample_api: ApiDefinition) -> None:
    results = [
        HealthProbeResult(
            api_id=sample_api.id,
            endpoint_name="Ping",
            url="https://example.com/api/ping",
            status_code=200,
            latency_ms=3500.0,  # exceeds 3000ms threshold
            is_healthy=True,
        )
    ]
    status = evaluate_service_status(sample_api, results)
    assert status.state == "degraded"


def test_evaluate_service_status_history_streak(sample_api: ApiDefinition) -> None:
    history = [
        {"date": "2026-11-14", "is_healthy": True, "latency_ms": 120.0},
        {"date": "2026-11-15", "is_healthy": True, "latency_ms": 110.0},
    ]
    results = [
        HealthProbeResult(
            api_id=sample_api.id,
            endpoint_name="Ping",
            url="https://example.com/api/ping",
            status_code=200,
            latency_ms=105.0,
            is_healthy=True,
        )
    ]
    status = evaluate_service_status(sample_api, results, historical_records=history)
    assert status.current_streak_days == 3
    assert status.uptime_7d_percent == 100.0
