"""Unit tests for static website generation."""

from pathlib import Path

from apivitals.loader import load_catalog
from apivitals.models import ServiceStatus
from apivitals.site_generator import build_site
from apivitals.storage import compute_vitals_summary


def test_build_site(tmp_path: Path) -> None:
    catalog = load_catalog("apis")
    services = [
        ServiceStatus(
            api_id=catalog.apis[0].id,
            name=catalog.apis[0].name,
            category=catalog.apis[0].category,
            state="healthy",
            latency_ms=80.0,
            status_code=200,
            cors_supported=True,
            last_checked="2026-11-16T00:00:00Z",
        )
    ]
    summary = compute_vitals_summary(services)
    site_dir = tmp_path / "site"

    build_site(catalog, summary, output_dir=site_dir, assets_dir="assets", data_dir="data")

    assert (site_dir / "index.html").is_file()
    assert (site_dir / "style.css").is_file()
    assert (site_dir / "app.js").is_file()

    html = (site_dir / "index.html").read_text(encoding="utf-8")
    assert "ApiVitals" in html
    assert "The Living Health Radar for Free Public APIs" in html
