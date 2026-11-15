"""Digest generator for STATUS.md, weekly reports, and README stats synchronization."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from apivitals.models import ApiCatalog, NetworkVitalsSummary


def generate_status_markdown(summary: NetworkVitalsSummary) -> str:
    """Generate STATUS.md containing real-time health tables and network vitals."""
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# ApiVitals Network Status & Reliability Radar",
        "",
        f"> **Last Verified:** `{now_str}` | **Total Monitored:** `{summary.total_monitored}` | "
        f"**Healthy:** `{summary.healthy_count}` | **Degraded:** `{summary.degraded_count}` | "
        f"**Offline:** `{summary.offline_count}`",
        "",
        "## Performance Snapshot",
        "",
        "| Metric | Current Value | Target Threshold |",
        "|:---|:---:|:---:|",
        f"| **Overall Network Uptime** | `{summary.overall_uptime_pct}%` | `>= 98.0%` |",
        f"| **Average Response Latency** | `{summary.avg_latency_ms} ms` | `< 800 ms` |",
        f"| **P95 Response Latency** | `{summary.p95_latency_ms} ms` | `< 2500 ms` |",
        "",
        "## Monitored Public APIs",
        "",
        "| API Name | Category | Status | Latency | 7-Day Uptime | CORS | SSL Expiry |",
        "|:---|:---|:---:|:---:|:---:|:---:|:---:|",
    ]

    # Sort: healthy first, then by latency
    sorted_services = sorted(
        summary.services,
        key=lambda s: (
            0 if s.state == "healthy" else (1 if s.state == "degraded" else 2),
            s.latency_ms,
        ),
    )

    for s in sorted_services:
        if s.state == "healthy":
            status_badge = "🟢 Healthy"
        elif s.state == "degraded":
            status_badge = "🟡 Degraded"
        elif s.state == "offline":
            status_badge = "🔴 Offline"
        else:
            status_badge = "⚪ Unknown"

        cors_badge = "✅ Yes" if s.cors_supported else "❌ No"
        ssl_str = f"{s.ssl_days_remaining}d" if s.ssl_days_remaining is not None else "N/A"

        lines.append(
            f"| **{s.name}** | `{s.category}` | {status_badge} | `{s.latency_ms} ms` | "
            f"`{s.uptime_7d_percent}%` | {cors_badge} | `{ssl_str}` |"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "*Status checks run daily via GitHub Actions. "
            "Want to add your public API? Submit a YAML definition in `apis/<category>/`.*",
            "",
        ]
    )

    return "\n".join(lines)


def write_status_file(summary: NetworkVitalsSummary, path: str | Path = "STATUS.md") -> None:
    """Save generated status table to STATUS.md."""
    content = generate_status_markdown(summary)
    Path(path).write_text(content, encoding="utf-8")


def generate_weekly_digest(catalog: ApiCatalog, summary: NetworkVitalsSummary) -> tuple[str, str]:
    """Generate weekly digest markdown report. Returns (filename, content)."""
    now = datetime.now(timezone.utc)
    year, week, _ = now.isocalendar()
    filename = f"digest-{year}-W{week:02d}.md"

    # Top 5 fastest
    healthy = [s for s in summary.services if s.state == "healthy" and s.latency_ms > 0]
    fastest = sorted(healthy, key=lambda s: s.latency_ms)[:5]

    # Uptime champions (100% 7d uptime and highest streak)
    champions = sorted(
        [s for s in summary.services if s.uptime_7d_percent >= 100.0],
        key=lambda s: s.current_streak_days,
        reverse=True,
    )[:5]

    # Degraded or offline
    issues = [s for s in summary.services if s.state in ("degraded", "offline")]

    lines = [
        f"# ApiVitals Weekly Intelligence Digest — Week {week}, {year}",
        "",
        f"> Published on {now.strftime('%B %d, %Y')} | Generated automatically by ApiVitals",
        "",
        "## Executive Summary",
        "",
        f"- **Monitored APIs:** {summary.total_monitored}",
        f"- **Network-wide Uptime:** {summary.overall_uptime_pct}%",
        f"- **Average Network Latency:** {summary.avg_latency_ms} ms (P95: {summary.p95_latency_ms} ms)",
        f"- **Healthy Services:** {summary.healthy_count} / {summary.total_monitored}",
        "",
        "## Top 5 Fastest Responding APIs",
        "",
        "| Rank | API Name | Category | Average Latency | CORS |",
        "|:---:|:---|:---|:---:|:---:|",
    ]

    for rank, s in enumerate(fastest, 1):
        cors_str = "Yes" if s.cors_supported else "No"
        lines.append(
            f"| #{rank} | **{s.name}** | `{s.category}` | `{s.latency_ms} ms` | {cors_str} |"
        )

    lines.extend(
        [
            "",
            "## Reliability Champions (100% 7-Day Uptime)",
            "",
            "| API Name | Category | Current Streak | Latency |",
            "|:---|:---|:---:|:---:|",
        ]
    )

    for s in champions:
        lines.append(
            f"| **{s.name}** | `{s.category}` | `{s.current_streak_days} days` | `{s.latency_ms} ms` |"
        )

    if issues:
        lines.extend(
            [
                "",
                "## Incidents & Degraded Endpoints",
                "",
                "| API Name | State | Status Code | Error Detail |",
                "|:---|:---:|:---:|:---|",
            ]
        )
        for s in issues:
            code_str = str(s.status_code) if s.status_code else "None"
            detail = s.error_detail or "Latency threshold exceeded"
            lines.append(f"| **{s.name}** | `{s.state}` | `{code_str}` | {detail} |")
    else:
        lines.extend(
            [
                "",
                "## Incidents & Degraded Endpoints",
                "",
                "🎉 **Zero active incidents.** All monitored APIs performed within normal parameters.",
            ]
        )

    lines.extend(
        [
            "",
            "---",
            "*Automated report generated by [ApiVitals](https://github.com/apivitals/apivitals).*",
        ]
    )

    return filename, "\n".join(lines)


def update_readme_stats(
    summary: NetworkVitalsSummary, readme_path: str | Path = "README.md"
) -> bool:
    """Synchronize dynamic stats section between <!-- STATS:START --> and <!-- STATS:END --> in README.md."""
    path = Path(readme_path)
    if not path.is_file():
        return False

    content = path.read_text(encoding="utf-8")
    start_tag = "<!-- STATS:START -->"
    end_tag = "<!-- STATS:END -->"

    if start_tag not in content or end_tag not in content:
        return False

    now_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    replacement = f"""{start_tag}
| Monitored APIs | Global Uptime | Average Latency | P95 Latency | Verified As Of |
|:---:|:---:|:---:|:---:|:---:|
| **{summary.total_monitored}** | **{summary.overall_uptime_pct}%** | **{summary.avg_latency_ms} ms** | **{summary.p95_latency_ms} ms** | **{now_date}** |
{end_tag}"""

    pattern = re.compile(f"{re.escape(start_tag)}.*?{re.escape(end_tag)}", re.DOTALL)
    new_content = pattern.sub(replacement, content)

    if new_content != content:
        path.write_text(new_content, encoding="utf-8")
        return True
    return False
