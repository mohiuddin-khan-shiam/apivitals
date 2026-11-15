# Contributing to ApiVitals

First off, thank you for considering contributing to **ApiVitals**! Projects like this rely entirely on open-source community support.

---

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

---

## Ways to Contribute

1. **Add a New Public API**: Submit a declarative YAML file in `apis/<category>/<api-slug>.yaml`.
2. **Report a Broken Endpoint**: If an API changed its URL or rate limits, submit an issue or PR updating its YAML specification.
3. **Enhance the Tooling / CLI**: Improve the Python CLI, add new export formats, or optimize probe concurrency.
4. **Improve the Dashboard**: Enhance the static GitHub Pages web dashboard (e.g. accessibility, UI components, charts).

---

## Adding a New Public API

Adding an API is designed to be frictionless:

1. Create a branch:
   ```bash
   git checkout -b add-my-api
   ```
2. Create `apis/<category>/<api-slug>.yaml`:
   ```yaml
   id: my-api
   name: My Cool Public API
   description: One-sentence description of what this API provides.
   category: Developer Tools
   homepage: https://example.com
   documentation: https://example.com/docs
   auth: none # none | api_key | oauth2
   https: true
   cors: true
   endpoints:
     - name: Sample Endpoint
       path: https://api.example.com/v1/ping
       method: GET
       expected_status: 200
       expected_content_type: json
   tags:
     - utility
     - developer-tools
   license: MIT
   rate_limit: 100 requests/minute
   ```
3. Validate your definition locally:
   ```bash
   uv run apivitals validate
   ```
4. Test probing your endpoint:
   ```bash
   uv run apivitals probe my-api
   ```
5. Commit and open a Pull Request!

---

## Local Development Workflow

We use [uv](https://docs.astral.sh/uv/) for blazing-fast dependency management:

```bash
# Clone the repo
git clone https://github.com/apivitals/apivitals.git
cd apivitals

# Install development environment
uv sync --extra dev

# Run test suite
uv run pytest

# Check formatting and linting
uv run ruff check .
uv run ruff format --check .

# Run static type checks
uv run mypy apivitals
```

---

## Pull Request Guidelines

- Ensure `uv run apivitals validate` passes without warnings.
- Keep commits descriptive and follow [Conventional Commits](https://www.conventionalcommits.org/) (e.g., `feat: add cat facts api`, `fix: update open-library endpoint`).
- Add or update tests whenever you modify core Python logic.
