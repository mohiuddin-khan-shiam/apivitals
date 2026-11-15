"""Asynchronous and synchronous network probe engine for API health and vitals."""

from __future__ import annotations

import asyncio
import socket
import ssl
import time
from contextlib import nullcontext
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx

from apivitals.models import (
    ApiCatalog,
    ApiDefinition,
    ApiEndpoint,
    HealthProbeResult,
    ServiceStatus,
    StatusState,
)

DEFAULT_USER_AGENT = (
    "ApiVitals-HealthCheck/1.0 (+https://github.com/mohiuddin-khan-shiam/apivitals)"
)
DEFAULT_TIMEOUT_SECONDS = 10.0
MAX_CONCURRENT_PROBES = 10


def check_ssl_expiry(
    hostname: str, port: int = 443, timeout: float = 3.0
) -> tuple[bool, int | None]:
    """Inspect SSL certificate validity and calculate days until expiration."""
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                if not cert or "notAfter" not in cert:
                    return False, None
                # Format: 'Nov 15 12:00:00 2026 GMT'
                expire_str = cert["notAfter"]
                if not isinstance(expire_str, str):
                    return False, None
                expire_date = datetime.strptime(expire_str, "%b %d %H:%M:%S %Y %Z").replace(
                    tzinfo=timezone.utc
                )
                now = datetime.now(timezone.utc)
                days_left = (expire_date - now).days
                return True, max(0, days_left)
    except Exception:
        return False, None


async def probe_endpoint_async(
    api_id: str,
    endpoint: ApiEndpoint,
    client: httpx.AsyncClient,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> HealthProbeResult:
    """Execute an asynchronous probe against an API endpoint."""
    url = endpoint.path
    parsed = urlparse(url)
    is_https = parsed.scheme.lower() == "https"
    ssl_valid = False
    ssl_days: int | None = None

    if is_https and parsed.hostname:
        # Check SSL certificate in a worker thread to keep event loop responsive
        try:
            loop = asyncio.get_running_loop()
            port = parsed.port or 443
            ssl_valid, ssl_days = await loop.run_in_executor(
                None, check_ssl_expiry, parsed.hostname, port, 3.0
            )
        except Exception:
            ssl_valid, ssl_days = False, None

    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://apivitals.dev",
        **endpoint.headers,
    }

    start_time = time.perf_counter()
    status_code: int | None = None
    cors_detected = False
    error_message: str | None = None
    is_healthy = False

    try:
        response = await client.request(
            method=endpoint.method,
            url=url,
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
        )
        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        status_code = response.status_code

        # Check CORS headers
        allow_origin = response.headers.get("access-control-allow-origin", "")
        if allow_origin in ("*", "https://apivitals.dev") or allow_origin:
            cors_detected = True

        # Check content type if specified
        content_type_ok = True
        if endpoint.expected_content_type:
            actual_ct = response.headers.get("content-type", "").lower()
            if endpoint.expected_content_type.lower() not in actual_ct:
                content_type_ok = False

        if status_code == endpoint.expected_status and content_type_ok:
            is_healthy = True
        elif 200 <= status_code < 400 and content_type_ok:
            # Tolerant 2xx/3xx fallback
            is_healthy = True
        elif not content_type_ok:
            actual_ct = response.headers.get("content-type", "none")
            error_message = f"Content-type mismatch: got '{actual_ct}', expected '{endpoint.expected_content_type}'"
        else:
            error_message = f"Unexpected status {status_code} (expected {endpoint.expected_status})"

    except httpx.TimeoutException:
        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        error_message = f"Request timed out after {timeout}s"
    except httpx.HTTPError as exc:
        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        error_message = f"HTTP error: {type(exc).__name__}: {str(exc)[:120]}"
    except Exception as exc:
        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        error_message = f"Probe error: {type(exc).__name__}: {str(exc)[:120]}"

    return HealthProbeResult(
        api_id=api_id,
        endpoint_name=endpoint.name,
        url=url,
        status_code=status_code,
        latency_ms=latency_ms,
        is_healthy=is_healthy,
        cors_detected=cors_detected,
        ssl_valid=ssl_valid if is_https else True,
        ssl_days_remaining=ssl_days,
        error_message=error_message,
    )


async def probe_api_async(
    api: ApiDefinition,
    client: httpx.AsyncClient | None = None,
    semaphore: asyncio.Semaphore | None = None,
) -> list[HealthProbeResult]:
    """Probe all endpoints defined for a specific API."""
    async with semaphore if semaphore else nullcontext():
        own_client = False
        if client is None:
            client = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_SECONDS)
            own_client = True

        try:
            results: list[HealthProbeResult] = []
            for ep in api.endpoints:
                res = await probe_endpoint_async(api.id, ep, client)
                results.append(res)
            return results
        finally:
            if own_client:
                await client.aclose()


async def probe_catalog_async(
    catalog: ApiCatalog,
    concurrency: int = MAX_CONCURRENT_PROBES,
) -> dict[str, list[HealthProbeResult]]:
    """Probe every API in the catalog concurrently with bounded concurrency."""
    semaphore = asyncio.Semaphore(concurrency)
    limits = httpx.Limits(max_keepalive_connections=20, max_connections=concurrency)

    async with httpx.AsyncClient(limits=limits, timeout=DEFAULT_TIMEOUT_SECONDS) as client:
        tasks = [probe_api_async(api, client=client, semaphore=semaphore) for api in catalog.apis]
        results_list = await asyncio.gather(*tasks, return_exceptions=False)

    return {api.id: results for api, results in zip(catalog.apis, results_list)}


def evaluate_service_status(
    api: ApiDefinition,
    probe_results: list[HealthProbeResult],
    historical_records: list[dict] | None = None,
) -> ServiceStatus:
    """Aggregate probe results and historical data into a comprehensive ServiceStatus."""
    if not probe_results:
        return ServiceStatus(
            api_id=api.id,
            name=api.name,
            category=api.category,
            state="unknown",
            latency_ms=0.0,
            status_code=None,
            cors_supported=api.cors,
            last_checked=datetime.now(timezone.utc).isoformat(),
            error_detail="No probe results available",
        )

    primary = probe_results[0]
    avg_latency = round(sum(r.latency_ms for r in probe_results) / len(probe_results), 2)
    all_healthy = all(r.is_healthy for r in probe_results)
    any_cors = any(r.cors_detected for r in probe_results)
    min_ssl_days = min(
        (r.ssl_days_remaining for r in probe_results if r.ssl_days_remaining is not None),
        default=None,
    )

    state: StatusState
    if all_healthy:
        if avg_latency > 3000.0:
            state = "degraded"
        else:
            state = "healthy"
    elif primary.status_code is not None and primary.status_code == 429:
        state = "degraded"
    else:
        state = "offline"

    # Compute uptime percentages from history
    uptime_7d = 100.0
    uptime_30d = 100.0
    streak = 1

    if historical_records:
        recent_7 = historical_records[-7:]
        recent_30 = historical_records[-30:]
        if recent_7:
            healthy_7 = sum(1 for r in recent_7 if r.get("is_healthy", False))
            uptime_7d = round((healthy_7 / len(recent_7)) * 100.0, 1)
        if recent_30:
            healthy_30 = sum(1 for r in recent_30 if r.get("is_healthy", False))
            uptime_30d = round((healthy_30 / len(recent_30)) * 100.0, 1)

        # Calculate streak backwards
        streak = 0
        for r in reversed(historical_records):
            if r.get("is_healthy", False):
                streak += 1
            else:
                break
        if all_healthy:
            streak += 1
    elif all_healthy:
        streak = 1
    else:
        streak = 0

    return ServiceStatus(
        api_id=api.id,
        name=api.name,
        category=api.category,
        state=state,
        latency_ms=avg_latency,
        status_code=primary.status_code,
        cors_supported=any_cors or api.cors,
        ssl_days_remaining=min_ssl_days,
        last_checked=datetime.now(timezone.utc).isoformat(),
        uptime_7d_percent=uptime_7d,
        uptime_30d_percent=uptime_30d,
        current_streak_days=streak,
        error_detail=primary.error_message,
    )


# Synchronous entrypoints
def probe_api(api: ApiDefinition) -> list[HealthProbeResult]:
    """Synchronous helper to probe an individual API."""
    return asyncio.run(probe_api_async(api))


def probe_catalog(
    catalog: ApiCatalog, concurrency: int = MAX_CONCURRENT_PROBES
) -> dict[str, list[HealthProbeResult]]:
    """Synchronous helper to probe an entire catalog."""
    return asyncio.run(probe_catalog_async(catalog, concurrency=concurrency))
