"""Command Line Interface for ApiVitals."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from apivitals import __version__
from apivitals.digest import (
    generate_weekly_digest,
    update_readme_stats,
    write_status_file,
)
from apivitals.loader import find_yaml_files, load_api_definition, load_catalog
from apivitals.models import ApiDefinition, ServiceStatus
from apivitals.prober import (
    evaluate_service_status,
    probe_api,
    probe_catalog,
)
from apivitals.site_generator import build_site
from apivitals.storage import (
    compute_vitals_summary,
    export_csv,
    export_json,
    export_sqlite,
    load_history,
    update_history,
)

console = Console()


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="apivitals")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """⚡ ApiVitals: The living health radar and curated directory of free public APIs."""
    if ctx.invoked_subcommand is None:
        console.print(
            Panel.fit(
                f"[bold cyan]ApiVitals[/bold cyan] [dim]v{__version__}[/dim]\n"
                "[green]The living health radar, latency benchmark, and curated directory of free public APIs.[/green]\n\n"
                "Run [bold yellow]apivitals --help[/bold yellow] for commands.",
                border_style="cyan",
            )
        )


@cli.command("validate")
@click.option("--apis-dir", default="apis", help="Directory containing API definition YAML files.")
def validate_command(apis_dir: str) -> None:
    """Validate all YAML definition files against the schema."""
    yaml_files = find_yaml_files(apis_dir)
    if not yaml_files:
        console.print(f"[yellow]Warning: No YAML files found in '{apis_dir}'[/yellow]")
        return

    console.print(f"Validating {len(yaml_files)} API definitions in '{apis_dir}'...")
    errors: list[tuple[Path, Exception]] = []
    seen_ids: dict[str, Path] = {}

    for path in yaml_files:
        try:
            api = load_api_definition(path)
            if api.id in seen_ids:
                errors.append(
                    (
                        path,
                        ValueError(
                            f"Duplicate id '{api.id}' also found in {seen_ids[api.id].name}"
                        ),
                    )
                )
            else:
                seen_ids[api.id] = path
        except Exception as e:
            errors.append((path, e))

    if errors:
        console.print(f"[bold red]Validation failed with {len(errors)} error(s):[/bold red]")
        for path, err in errors:
            console.print(f"  [red]✗[/red] {path}: {err}")
        sys.exit(1)
    else:
        console.print(
            f"[bold green]✓ All {len(yaml_files)} API definitions are valid![/bold green]"
        )


@cli.command("list")
@click.option("--category", default=None, help="Filter by category name.")
@click.option("--cors/--no-cors", default=None, help="Filter by CORS support.")
@click.option("--auth", default=None, help="Filter by auth type (none, api_key, oauth2).")
@click.option("--apis-dir", default="apis", help="Directory containing API YAML files.")
def list_command(category: str | None, cors: bool | None, auth: str | None, apis_dir: str) -> None:
    """List curated public APIs with filters."""
    catalog = load_catalog(apis_dir)

    apis = catalog.apis
    if category:
        apis = [a for a in apis if a.category.lower() == category.lower()]
    if cors is not None:
        apis = [a for a in apis if a.cors == cors]
    if auth:
        apis = [a for a in apis if a.auth.lower() == auth.lower()]

    table = Table(
        title=f"ApiVitals Public API Catalog ({len(apis)} entries)", header_style="bold cyan"
    )
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold white")
    table.add_column("Category", style="green")
    table.add_column("Auth", style="yellow")
    table.add_column("CORS", style="magenta")
    table.add_column("Rate Limit", style="dim")

    for a in apis:
        cors_str = "[green]Yes[/green]" if a.cors else "[red]No[/red]"
        auth_str = "[green]None[/green]" if a.auth == "none" else f"[yellow]{a.auth}[/yellow]"
        table.add_row(a.id, a.name, a.category, auth_str, cors_str, a.rate_limit)

    console.print(table)


@cli.command("search")
@click.argument("query")
@click.option("--category", default=None, help="Filter by category.")
@click.option("--cors-only", is_flag=True, help="Only show CORS-enabled APIs.")
@click.option("--apis-dir", default="apis", help="Directory containing API YAML files.")
def search_command(query: str, category: str | None, cors_only: bool, apis_dir: str) -> None:
    """Search APIs by keyword in name, description, tags, or endpoints."""
    catalog = load_catalog(apis_dir)
    q = query.lower()

    matches: list[ApiDefinition] = []
    for a in catalog.apis:
        if category and a.category.lower() != category.lower():
            continue
        if cors_only and not a.cors:
            continue

        in_name = q in a.name.lower()
        in_desc = q in a.description.lower()
        in_tags = any(q in t.lower() for t in a.tags)
        in_eps = any(q in ep.path.lower() for ep in a.endpoints)

        if in_name or in_desc or in_tags or in_eps:
            matches.append(a)

    if not matches:
        console.print(f"[yellow]No APIs found matching query '[bold]{query}[/bold]'[/yellow]")
        return

    table = Table(
        title=f"Search Results for '{query}' ({len(matches)} found)", header_style="bold cyan"
    )
    table.add_column("API Name", style="bold white")
    table.add_column("Category", style="green")
    table.add_column("Description", style="dim")
    table.add_column("Docs Link", style="blue")

    for a in matches:
        table.add_row(a.name, a.category, a.description[:60] + "...", a.documentation)

    console.print(table)


@cli.command("probe")
@click.argument("api_id", required=False)
@click.option("--apis-dir", default="apis", help="Directory containing API YAML files.")
def probe_command(api_id: str | None, apis_dir: str) -> None:
    """Execute live network health probe against one or all APIs."""
    catalog = load_catalog(apis_dir)

    if api_id:
        target = next((a for a in catalog.apis if a.id == api_id), None)
        if not target:
            console.print(f"[bold red]Error: API id '{api_id}' not found.[/bold red]")
            sys.exit(1)
        console.print(f"Probing API [cyan]{target.name}[/cyan] ({target.id})...")
        results = probe_api(target)
        status = evaluate_service_status(target, results)

        state_color = (
            "green"
            if status.state == "healthy"
            else ("yellow" if status.state == "degraded" else "red")
        )
        console.print(f"State: [{state_color}]{status.state.upper()}[/{state_color}]")
        console.print(f"Latency: {status.latency_ms} ms")
        console.print(f"HTTP Status: {status.status_code}")
        console.print(f"CORS Detected: {status.cors_supported}")
        if status.ssl_days_remaining is not None:
            console.print(f"SSL Cert Expiry: {status.ssl_days_remaining} days remaining")
        if status.error_detail:
            console.print(f"[red]Error Detail: {status.error_detail}[/red]")
        return

    console.print(f"Executing live probes across all {len(catalog.apis)} catalog APIs...")
    probe_results_map = probe_catalog(catalog)
    services: list[ServiceStatus] = []

    for a in catalog.apis:
        res = probe_results_map.get(a.id, [])
        st = evaluate_service_status(a, res)
        services.append(st)

    summary = compute_vitals_summary(services)
    table = Table(
        title=f"ApiVitals Probe Results ({summary.total_monitored} probed)",
        header_style="bold cyan",
    )
    table.add_column("API Name", style="bold white")
    table.add_column("State", justify="center")
    table.add_column("Latency", justify="right")
    table.add_column("HTTP Code", justify="center")
    table.add_column("CORS", justify="center")

    for s in services:
        state_str = (
            "[green]HEALTHY[/green]"
            if s.state == "healthy"
            else ("[yellow]DEGRADED[/yellow]" if s.state == "degraded" else "[red]OFFLINE[/red]")
        )
        cors_str = "[green]✓[/green]" if s.cors_supported else "[dim]✗[/dim]"
        code_str = str(s.status_code) if s.status_code else "-"
        table.add_row(s.name, state_str, f"{s.latency_ms} ms", code_str, cors_str)

    console.print(table)
    console.print(
        f"\n[bold]Overall Uptime:[/bold] {summary.overall_uptime_pct}% | [bold]Avg Latency:[/bold] {summary.avg_latency_ms} ms | [bold]P95:[/bold] {summary.p95_latency_ms} ms"
    )


@cli.command("stats")
@click.option("--status-file", default="data/status.json", help="Path to status.json file.")
def stats_command(status_file: str) -> None:
    """Display overall network vitals and reliability statistics."""
    path = Path(status_file)
    if not path.is_file():
        console.print(
            f"[yellow]Status file '{status_file}' does not exist yet. Run 'apivitals update' first.[/yellow]"
        )
        return

    import json

    data = json.loads(path.read_text(encoding="utf-8"))
    summary = compute_vitals_summary(
        [ServiceStatus.model_validate(s) for s in data.get("services", [])]
    )

    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column()
    grid.add_column()

    grid.add_row("[bold cyan]Total APIs Monitored:[/bold cyan]", str(summary.total_monitored))
    grid.add_row(
        "[bold green]Healthy APIs:[/bold green]",
        f"{summary.healthy_count} ({(summary.healthy_count / (summary.total_monitored or 1)) * 100:.1f}%)",
    )
    grid.add_row("[bold yellow]Degraded APIs:[/bold yellow]", str(summary.degraded_count))
    grid.add_row("[bold red]Offline APIs:[/bold red]", str(summary.offline_count))
    grid.add_row(
        "[bold magenta]Global Network Uptime:[/bold magenta]", f"{summary.overall_uptime_pct}%"
    )
    grid.add_row("[bold blue]Average Latency:[/bold blue]", f"{summary.avg_latency_ms} ms")
    grid.add_row("[bold purple]P95 Latency:[/bold purple]", f"{summary.p95_latency_ms} ms")

    console.print(
        Panel(
            grid, title="[bold]ApiVitals Global Performance Statistics[/bold]", border_style="cyan"
        )
    )


@cli.command("export")
@click.option("--format", "fmt", type=click.Choice(["json", "csv", "sqlite", "all"]), default="all")
@click.option("--apis-dir", default="apis", help="Directory containing API YAML files.")
@click.option("--output-dir", default="data", help="Output directory for generated datasets.")
def export_command(fmt: str, apis_dir: str, output_dir: str) -> None:
    """Export catalog and health records to JSON, CSV, or SQLite."""
    catalog = load_catalog(apis_dir)
    history = load_history(f"{output_dir}/history.json")

    # Load existing status or generate default
    status_path = Path(output_dir) / "status.json"
    services: list[ServiceStatus] = []
    if status_path.is_file():
        import json

        st_data = json.loads(status_path.read_text(encoding="utf-8"))
        services = [ServiceStatus.model_validate(s) for s in st_data.get("services", [])]
    else:
        for a in catalog.apis:
            services.append(evaluate_service_status(a, []))

    summary = compute_vitals_summary(services)

    if fmt in ("json", "all"):
        export_json(catalog, summary, output_dir=output_dir)
        console.print(
            f"[green]✓ Exported {output_dir}/catalog.json & {output_dir}/status.json[/green]"
        )

    if fmt in ("csv", "all"):
        export_csv(catalog, summary, output_path=f"{output_dir}/catalog.csv")
        console.print(f"[green]✓ Exported {output_dir}/catalog.csv[/green]")

    if fmt in ("sqlite", "all"):
        export_sqlite(catalog, summary, history, output_path=f"{output_dir}/catalog.db")
        console.print(f"[green]✓ Exported {output_dir}/catalog.db[/green]")


@cli.command("update")
@click.option("--apis-dir", default="apis", help="Directory containing API YAML files.")
@click.option("--data-dir", default="data", help="Directory for storing datasets.")
@click.option("--site-dir", default="site", help="Directory for static website build.")
@click.option("--skip-probes", is_flag=True, help="Skip network probes (offline mode for testing).")
def update_command(apis_dir: str, data_dir: str, site_dir: str, skip_probes: bool) -> None:
    """Full automated maintenance pipeline: probe, export datasets, update status, and rebuild site."""
    console.print("[bold cyan]Starting ApiVitals automated pipeline...[/bold cyan]")

    # 1. Load catalog
    catalog = load_catalog(apis_dir)
    console.print(f"Loaded {len(catalog.apis)} APIs across {len(catalog.categories)} categories.")

    # 2. Probe endpoints
    history = load_history(f"{data_dir}/history.json")
    services: list[ServiceStatus] = []

    if skip_probes:
        console.print(
            "[yellow]Skipping network probes (offline mode). Using cached baseline.[/yellow]"
        )
        status_path = Path(data_dir) / "status.json"
        cached_map: dict[str, ServiceStatus] = {}
        if status_path.is_file():
            import json

            st_data = json.loads(status_path.read_text(encoding="utf-8"))
            for s_dict in st_data.get("services", []):
                s_obj = ServiceStatus.model_validate(s_dict)
                cached_map[s_obj.api_id] = s_obj

        for a in catalog.apis:
            if a.id in cached_map:
                services.append(cached_map[a.id])
            else:
                svc_history = history.get(a.id, [])
                services.append(evaluate_service_status(a, [], svc_history))
    else:
        console.print("Executing asynchronous network probes against all endpoints...")
        probe_results_map = probe_catalog(catalog)
        for a in catalog.apis:
            res = probe_results_map.get(a.id, [])
            svc_history = history.get(a.id, [])
            st = evaluate_service_status(a, res, historical_records=svc_history)
            services.append(st)

    summary = compute_vitals_summary(services)
    console.print(
        f"[green]Probes complete: {summary.healthy_count} healthy, "
        f"{summary.degraded_count} degraded, {summary.offline_count} offline. "
        f"Uptime: {summary.overall_uptime_pct}%, Avg Latency: {summary.avg_latency_ms} ms.[/green]"
    )

    # 3. Update rolling history
    history = update_history(services, history_file=f"{data_dir}/history.json")

    # 4. Export JSON, CSV, SQLite
    export_json(catalog, summary, output_dir=data_dir)
    export_csv(catalog, summary, output_path=f"{data_dir}/catalog.csv")
    export_sqlite(catalog, summary, history, output_path=f"{data_dir}/catalog.db")
    console.print("[green]Exported catalog.json, status.json, catalog.csv, and catalog.db.[/green]")

    # 5. Write STATUS.md
    write_status_file(summary, path="STATUS.md")
    console.print("[green]Updated STATUS.md with live table.[/green]")

    # 6. Update README stats markers
    if update_readme_stats(summary, readme_path="README.md"):
        console.print("[green]Updated README.md dynamic stats markers.[/green]")

    # 7. Build static website
    build_site(catalog, summary, output_dir=site_dir, assets_dir="assets", data_dir=data_dir)
    console.print(f"[green]Built static dashboard in '{site_dir}' for GitHub Pages.[/green]")

    console.print("[bold green]✓ ApiVitals pipeline completed successfully![/bold green]")


@cli.command("digest")
@click.option("--apis-dir", default="apis", help="Directory containing API YAML files.")
@click.option("--status-file", default="data/status.json", help="Path to status.json.")
@click.option("--reports-dir", default="reports", help="Directory to save weekly digest.")
def digest_command(apis_dir: str, status_file: str, reports_dir: str) -> None:
    """Generate weekly performance and reliability intelligence report."""
    catalog = load_catalog(apis_dir)
    path = Path(status_file)
    if not path.is_file():
        console.print(
            f"[bold red]Error: '{status_file}' does not exist. Run 'apivitals update' first.[/bold red]"
        )
        sys.exit(1)

    import json

    st_data = json.loads(path.read_text(encoding="utf-8"))
    summary = compute_vitals_summary(
        [ServiceStatus.model_validate(s) for s in st_data.get("services", [])]
    )

    rep_dir = Path(reports_dir)
    rep_dir.mkdir(parents=True, exist_ok=True)

    filename, content = generate_weekly_digest(catalog, summary)
    out_file = rep_dir / filename
    out_file.write_text(content, encoding="utf-8")

    console.print(f"[bold green]✓ Generated weekly digest at {out_file}[/bold green]")


def main() -> None:
    """Entry point for console script."""
    cli()


if __name__ == "__main__":
    main()
