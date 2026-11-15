"""Test suite validating GitHub Actions workflow YAML syntax and configuration."""

from pathlib import Path

import yaml


def test_workflows_syntax() -> None:
    workflows_dir = Path(".github/workflows")
    assert workflows_dir.is_dir()
    workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    assert len(workflow_files) >= 5

    for wf in workflow_files:
        content = wf.read_text(encoding="utf-8")
        parsed = yaml.safe_load(content)
        assert isinstance(parsed, dict), f"{wf.name} should parse to a dictionary"
        assert "name" in parsed, f"{wf.name} should define a top-level 'name'"
        assert "jobs" in parsed, f"{wf.name} should define 'jobs'"


def test_issue_templates_syntax() -> None:
    template_dir = Path(".github/ISSUE_TEMPLATE")
    assert template_dir.is_dir()
    templates = list(template_dir.glob("*.yml"))
    assert len(templates) >= 3

    for tmpl in templates:
        content = tmpl.read_text(encoding="utf-8")
        parsed = yaml.safe_load(content)
        assert isinstance(parsed, dict)
