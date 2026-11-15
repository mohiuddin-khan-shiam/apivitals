"""Loader and validator for curated YAML API definitions."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from apivitals.models import ApiCatalog, ApiDefinition


def find_yaml_files(base_dir: str | Path) -> list[Path]:
    """Recursively discover all YAML definition files within base_dir."""
    root = Path(base_dir)
    if not root.is_dir():
        return []
    files: list[Path] = []
    for ext in ("*.yaml", "*.yml"):
        files.extend(root.rglob(ext))
    return sorted(files)


def load_api_definition(file_path: str | Path) -> ApiDefinition:
    """Load and validate a single API definition YAML file."""
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"File {path.name} must contain a YAML mapping (dictionary)")

    try:
        return ApiDefinition.model_validate(data)
    except ValidationError as e:
        raise ValueError(f"Validation error in {path}: {e}") from e


def load_catalog(apis_dir: str | Path = "apis") -> ApiCatalog:
    """Load all API definitions from directory and construct an ApiCatalog."""
    yaml_files = find_yaml_files(apis_dir)
    apis: list[ApiDefinition] = []
    seen_ids: set[str] = set()
    categories_set: set[str] = set()

    for path in yaml_files:
        api = load_api_definition(path)
        if api.id in seen_ids:
            raise ValueError(f"Duplicate API id detected: '{api.id}' in {path}")
        seen_ids.add(api.id)
        categories_set.add(api.category)
        apis.append(api)

    apis.sort(key=lambda x: (x.category, x.name))
    categories = sorted(categories_set)

    return ApiCatalog(
        total_apis=len(apis),
        categories=categories,
        apis=apis,
    )
