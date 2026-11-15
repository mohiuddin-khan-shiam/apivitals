.PHONY: install test lint format typecheck validate update clean help

help:
	@echo "Available commands:"
	@echo "  make install    - Install project dependencies with uv"
	@echo "  make test       - Run pytest test suite"
	@echo "  make lint       - Run ruff linter check"
	@echo "  make format     - Run ruff format and fix"
	@echo "  make typecheck  - Run mypy type checker"
	@echo "  make validate   - Validate all API YAML definition files"
	@echo "  make update     - Run full automated health check and update pipeline"
	@echo "  make clean      - Clean virtualenv caches and build artifacts"

install:
	uv sync --extra dev

test:
	uv run pytest -m "not network"

test-all:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .
	uv run ruff check --fix .

typecheck:
	uv run mypy apivitals

validate:
	uv run apivitals validate

update:
	uv run apivitals update

clean:
	rm -rf .venv .pytest_cache .mypy_cache .ruff_cache dist build *.egg-info
