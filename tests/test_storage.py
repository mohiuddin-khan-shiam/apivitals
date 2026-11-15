"""Unit tests for dataset export layer in JSON, CSV, and SQLite."""

import json
import sqlite3
from pathlib import Path

from apivitals.loader import load_catalog
from apivitals.models import ServiceStatus
from apivitals.storage import (
    compute_vitals_summary,
    export_csv,
    export_json,
    export_sqlite,
    update_history,
)


def test_export_json_and_summary(tmp_path: Path) -> None:
    catalog = load_catalog("apis")
    services = [
        ServiceStatus(
            api_id="open-meteo",
            name="Open-Meteo",
            category="Weather & Climate",
            state="healthy",
            latency_ms=130.0,
            status_code=200,
            cors_supported=True,
            last_checked="2026-11-16T00:00:00Z",
        )
    ]
    summary = compute_vitals_summary(services)
    export_json(catalog, summary, output_dir=tmp_path)

    assert (tmp_path / "catalog.json").is_file()
    assert (tmp_path / "status.json").is_file()

    status_data = json.loads((tmp_path / "status.json").read_text(encoding="utf-8"))
    assert status_data["total_monitored"] == 1
    assert status_data["overall_uptime_pct"] == 100.0


def test_export_csv(tmp_path: Path) -> None:
    catalog = load_catalog("apis")
    services = [
        ServiceStatus(
            api_id=catalog.apis[0].id,
            name=catalog.apis[0].name,
            category=catalog.apis[0].category,
            state="healthy",
            latency_ms=95.0,
            status_code=200,
            cors_supported=True,
            last_checked="2026-11-16T00:00:00Z",
        )
    ]
    summary = compute_vitals_summary(services)
    csv_file = tmp_path / "catalog.csv"
    export_csv(catalog, summary, output_path=csv_file)

    assert csv_file.is_file()
    lines = csv_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) >= 2  # header + at least 1 entry
    assert "id,name,category,state" in lines[0]


def test_export_sqlite(tmp_path: Path) -> None:
    catalog = load_catalog("apis")
    services = [
        ServiceStatus(
            api_id=catalog.apis[0].id,
            name=catalog.apis[0].name,
            category=catalog.apis[0].category,
            state="healthy",
            latency_ms=95.0,
            status_code=200,
            cors_supported=True,
            last_checked="2026-11-16T00:00:00Z",
        )
    ]
    summary = compute_vitals_summary(services)
    db_file = tmp_path / "catalog.db"
    history = {catalog.apis[0].id: [{"date": "2026-11-16", "is_healthy": True, "latency_ms": 95.0}]}

    export_sqlite(catalog, summary, history, output_path=db_file)
    assert db_file.is_file()

    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM apis")
    count_apis = cur.fetchone()[0]
    assert count_apis == len(catalog.apis)

    cur.execute("SELECT latency_ms FROM status WHERE api_id = ?", (catalog.apis[0].id,))
    val = cur.fetchone()[0]
    assert val == 95.0
    conn.close()


def test_update_history_pruning(tmp_path: Path) -> None:
    hist_file = tmp_path / "history.json"
    services = [
        ServiceStatus(
            api_id="test-svc",
            name="Test",
            category="Test",
            state="healthy",
            latency_ms=50.0,
            status_code=200,
            cors_supported=True,
            last_checked="2026-11-16T00:00:00Z",
        )
    ]
    hist = update_history(services, history_file=hist_file, max_days=7)
    assert "test-svc" in hist
    assert len(hist["test-svc"]) == 1
    assert hist["test-svc"][0]["is_healthy"] is True
