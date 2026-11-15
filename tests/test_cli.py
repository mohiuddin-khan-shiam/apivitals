"""Unit tests for the ApiVitals Click CLI commands."""

from pathlib import Path

from click.testing import CliRunner

from apivitals.cli import cli


def test_cli_version() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_validate() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["validate", "--apis-dir", "apis"])
    assert result.exit_code == 0
    assert "All" in result.output
    assert "valid" in result.output


def test_cli_list() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "Open-Meteo" in result.output


def test_cli_search() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "weather"])
    assert result.exit_code == 0
    assert "Weather" in result.output


def test_cli_search_not_found() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "nonexistentquery12345"])
    assert result.exit_code == 0
    assert "No APIs found" in result.output


def test_cli_update_skip_probes(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "update",
            "--apis-dir",
            "apis",
            "--data-dir",
            str(tmp_path / "data"),
            "--site-dir",
            str(tmp_path / "site"),
            "--skip-probes",
        ],
    )
    assert result.exit_code == 0
    assert "pipeline completed successfully" in result.output
    assert (tmp_path / "data" / "catalog.json").is_file()
    assert (tmp_path / "site" / "index.html").is_file()


def test_cli_digest(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "digest",
            "--apis-dir",
            "apis",
            "--status-file",
            "data/status.json",
            "--reports-dir",
            str(tmp_path / "reports"),
        ],
    )
    assert result.exit_code == 0
    assert "Generated weekly digest" in result.output
