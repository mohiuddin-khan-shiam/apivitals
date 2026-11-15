"""Storage layer for exporting catalog and health vitals to JSON, CSV, and SQLite."""

from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from apivitals.models import (
    ApiCatalog,
    NetworkVitalsSummary,
    ServiceStatus,
)


def load_history(history_file: str | Path = "data/history.json") -> dict[str, list[dict]]:
    """Load historical probe records from JSON file."""
    path = Path(history_file)
    if not path.is_file():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def update_history(
    services: list[ServiceStatus],
    history_file: str | Path = "data/history.json",
    max_days: int = 30,
) -> dict[str, list[dict]]:
    """Append today's probe records to history and prune beyond max_days."""
    history = load_history(history_file)
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for svc in services:
        records = history.setdefault(svc.api_id, [])
        # Check if today is already recorded; if so, replace with latest
        record = {
            "date": today_str,
            "is_healthy": svc.state in ("healthy", "degraded"),
            "latency_ms": svc.latency_ms,
            "status_code": svc.status_code,
        }

        # Filter out existing today record if any
        records = [r for r in records if r.get("date") != today_str]
        records.append(record)
        # Keep last max_days
        history[svc.api_id] = records[-max_days:]

    # Save back to history_file
    path = Path(history_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    return history


def compute_vitals_summary(services: list[ServiceStatus]) -> NetworkVitalsSummary:
    """Compute global health, latency percentiles, and counts."""
    total = len(services)
    if total == 0:
        return NetworkVitalsSummary(
            total_monitored=0,
            healthy_count=0,
            degraded_count=0,
            offline_count=0,
            overall_uptime_pct=100.0,
            avg_latency_ms=0.0,
            p95_latency_ms=0.0,
            services=[],
        )

    healthy = sum(1 for s in services if s.state == "healthy")
    degraded = sum(1 for s in services if s.state == "degraded")
    offline = sum(1 for s in services if s.state == "offline")
    uptime_pct = round(((healthy + degraded) / total) * 100.0, 1)

    latencies = sorted(s.latency_ms for s in services if s.latency_ms > 0)
    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0

    if latencies:
        p95_index = int(len(latencies) * 0.95)
        p95_latency = latencies[min(p95_index, len(latencies) - 1)]
    else:
        p95_latency = 0.0

    return NetworkVitalsSummary(
        total_monitored=total,
        healthy_count=healthy,
        degraded_count=degraded,
        offline_count=offline,
        overall_uptime_pct=uptime_pct,
        avg_latency_ms=avg_latency,
        p95_latency_ms=p95_latency,
        services=services,
    )


def export_json(
    catalog: ApiCatalog,
    summary: NetworkVitalsSummary,
    output_dir: str | Path = "data",
) -> None:
    """Export catalog.json and status.json."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    catalog_path = out / "catalog.json"
    status_path = out / "status.json"

    with catalog_path.open("w", encoding="utf-8") as f:
        json.dump(catalog.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

    with status_path.open("w", encoding="utf-8") as f:
        json.dump(summary.model_dump(mode="json"), f, indent=2, ensure_ascii=False)


def export_csv(
    catalog: ApiCatalog,
    summary: NetworkVitalsSummary,
    output_path: str | Path = "data/catalog.csv",
) -> None:
    """Export flattened tabular view of catalog and status to CSV."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    status_map = {s.api_id: s for s in summary.services}

    fieldnames = [
        "id",
        "name",
        "category",
        "state",
        "latency_ms",
        "status_code",
        "uptime_7d_percent",
        "uptime_30d_percent",
        "current_streak_days",
        "auth",
        "https",
        "cors_supported",
        "ssl_days_remaining",
        "rate_limit",
        "license",
        "documentation",
        "homepage",
    ]

    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for api in catalog.apis:
            st = status_map.get(api.id)
            writer.writerow(
                {
                    "id": api.id,
                    "name": api.name,
                    "category": api.category,
                    "state": st.state if st else "unknown",
                    "latency_ms": st.latency_ms if st else 0.0,
                    "status_code": st.status_code if st else "",
                    "uptime_7d_percent": st.uptime_7d_percent if st else 100.0,
                    "uptime_30d_percent": st.uptime_30d_percent if st else 100.0,
                    "current_streak_days": st.current_streak_days if st else 0,
                    "auth": api.auth,
                    "https": api.https,
                    "cors_supported": st.cors_supported if st else api.cors,
                    "ssl_days_remaining": st.ssl_days_remaining
                    if (st and st.ssl_days_remaining is not None)
                    else "",
                    "rate_limit": api.rate_limit,
                    "license": api.license,
                    "documentation": api.documentation,
                    "homepage": api.homepage,
                }
            )


def export_sqlite(
    catalog: ApiCatalog,
    summary: NetworkVitalsSummary,
    history: dict[str, list[dict]],
    output_path: str | Path = "data/catalog.db",
) -> None:
    """Export catalog, current status, and history to SQLite database."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(out)
    cur = conn.cursor()

    # Create tables
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS apis (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            homepage TEXT,
            documentation TEXT,
            auth TEXT,
            https INTEGER,
            cors INTEGER,
            license TEXT,
            rate_limit TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS status (
            api_id TEXT PRIMARY KEY,
            state TEXT NOT NULL,
            latency_ms REAL,
            status_code INTEGER,
            cors_supported INTEGER,
            ssl_days_remaining INTEGER,
            last_checked TEXT,
            uptime_7d_percent REAL,
            uptime_30d_percent REAL,
            current_streak_days INTEGER,
            error_detail TEXT,
            FOREIGN KEY (api_id) REFERENCES apis(id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_id TEXT NOT NULL,
            date TEXT NOT NULL,
            is_healthy INTEGER NOT NULL,
            latency_ms REAL NOT NULL,
            status_code INTEGER,
            FOREIGN KEY (api_id) REFERENCES apis(id)
        )
        """
    )

    # Insert / replace apis
    for api in catalog.apis:
        cur.execute(
            """
            INSERT OR REPLACE INTO apis (
                id, name, category, description, homepage, documentation,
                auth, https, cors, license, rate_limit
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                api.id,
                api.name,
                api.category,
                api.description,
                api.homepage,
                api.documentation,
                api.auth,
                1 if api.https else 0,
                1 if api.cors else 0,
                api.license,
                api.rate_limit,
            ),
        )

    # Insert / replace status
    for s in summary.services:
        cur.execute(
            """
            INSERT OR REPLACE INTO status (
                api_id, state, latency_ms, status_code, cors_supported,
                ssl_days_remaining, last_checked, uptime_7d_percent,
                uptime_30d_percent, current_streak_days, error_detail
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                s.api_id,
                s.state,
                s.latency_ms,
                s.status_code,
                1 if s.cors_supported else 0,
                s.ssl_days_remaining,
                s.last_checked,
                s.uptime_7d_percent,
                s.uptime_30d_percent,
                s.current_streak_days,
                s.error_detail,
            ),
        )

    # Clear and insert history
    cur.execute("DELETE FROM history")
    for api_id, records in history.items():
        for r in records:
            cur.execute(
                """
                INSERT INTO history (api_id, date, is_healthy, latency_ms, status_code)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    api_id,
                    r.get("date", ""),
                    1 if r.get("is_healthy", False) else 0,
                    r.get("latency_ms", 0.0),
                    r.get("status_code"),
                ),
            )

    conn.commit()
    conn.close()
