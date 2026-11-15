"""Unit tests for YAML definition loader and catalog validation."""

from pathlib import Path

import pytest
import yaml

from apivitals.loader import load_api_definition, load_catalog


def test_load_real_catalog() -> None:
    catalog = load_catalog("apis")
    assert catalog.total_apis >= 20
    assert len(catalog.categories) >= 8
    assert all(a.id for a in catalog.apis)
    assert all(len(a.endpoints) >= 1 for a in catalog.apis)


def test_duplicate_id_detection(tmp_path: Path) -> None:
    api1 = {
        "id": "dup-api",
        "name": "API One",
        "description": "First",
        "category": "Test",
        "homepage": "https://example.com",
        "documentation": "https://example.com",
        "endpoints": [{"name": "P1", "path": "https://example.com/1"}],
    }
    api2 = {
        "id": "dup-api",
        "name": "API Two",
        "description": "Second",
        "category": "Test",
        "homepage": "https://example.com",
        "documentation": "https://example.com",
        "endpoints": [{"name": "P2", "path": "https://example.com/2"}],
    }
    (tmp_path / "a.yaml").write_text(yaml.dump(api1), encoding="utf-8")
    (tmp_path / "b.yaml").write_text(yaml.dump(api2), encoding="utf-8")

    with pytest.raises(ValueError, match="Duplicate API id detected"):
        load_catalog(tmp_path)


def test_invalid_yaml_format(tmp_path: Path) -> None:
    bad_file = tmp_path / "bad.yaml"
    bad_file.write_text("just a string, not a dictionary", encoding="utf-8")
    with pytest.raises(ValueError, match="must contain a YAML mapping"):
        load_api_definition(bad_file)
