FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project specification files
COPY pyproject.toml README.md ./

# Install production dependencies
RUN uv sync --no-dev

# Copy application source code and APIs
COPY apivitals ./apivitals
COPY apis ./apis
COPY assets ./assets

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["apivitals"]
CMD ["list"]
