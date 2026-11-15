"""Unit tests for status, weekly digest, and README stats synchronization."""

from pathlib import Path

from apivitals.digest import (
    generate_status_markdown,
    generate_weekly_digest,
    update_readme_stats,
)
from apivitals.loader import load_catalog
from apivitals.models import ServiceStatus
from apivitals.storage import compute_vitals_summary


def test_generate_status_markdown() -> None:
    services = [
        ServiceStatus(
            api_id="test-api",
            name="Test API",
            category="Developer Tools",
            state="healthy",
            latency_ms=105.0,
            status_code=200,
            cors_supported=True,
            ssl_days_remaining=120,
            last_checked="2026-11-16T00:00:00Z",
        )
    ]
    summary = compute_vitals_summary(services)
    md = generate_status_markdown(summary)
    assert "# ApiVitals Network Status & Reliability Radar" in md
    assert "Test API" in md
    assert "🟢 Healthy" in md
    assert "105.0 ms" in md


def test_generate_weekly_digest() -> None:
    catalog = load_catalog("apis")
    services = [
        ServiceStatus(
            api_id="fast-api",
            name="Fast API",
            category="Developer Tools",
            state="healthy",
            latency_ms=45.0,
            status_code=200,
            cors_supported=True,
            last_checked="2026-11-16T00:00:00Z",
        )
    ]
    summary = compute_vitals_summary(services)
    filename, content = generate_weekly_digest(catalog, summary)
    assert filename.startswith("digest-")
    assert "Weekly Intelligence Digest" in content
    assert "Fast API" in content


def test_update_readme_stats(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(
        "Header\n<!-- STATS:START -->\nold stats\n<!-- STATS:END -->\nFooter",
        encoding="utf-8",
    )
    services = [
        ServiceStatus(
            api_id="test",
            name="Test",
            category="Test",
            state="healthy",
            latency_ms=50.0,
            status_code=200,
            cors_supported=True,
            last_checked="2026-11-16T00:00:00Z",
        )
    ]
    summary = compute_vitals_summary(services)
    changed = update_readme_stats(summary, readme_path=readme)
    assert changed is True

    new_text = readme.read_text(encoding="utf-8")
    assert "old stats" not in new_text
    assert "Global Uptime" in new_text
