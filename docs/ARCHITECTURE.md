# ApiVitals Architecture & Design

This document details the engineering design, system components, data flow, and synthetic monitoring methodology of **ApiVitals**.

---

## 1. Design Principles

1. **Human Curated, Machine Audited**: Every API definition is vetted for relevance, clear licensing, and open accessibility. Machine automation continuously verifies uptime, latency, CORS, and SSL certificate health.
2. **Zero Runtime Bloat**: The client library and static web dashboard require zero external framework runtimes. The static web dashboard is built in pure semantic HTML5, CSS3, and vanilla modern JavaScript (< 40KB total).
3. **Reproducible & Offline-Friendly**: All datasets are stored locally in version control as standard JSON, CSV, and SQLite. The CLI works offline against cached catalog data.
4. **Polite Synthetic Probing**: Synthetic probes respect rate limits, execute at most once per day, use generous timeouts (5–7s), and identify themselves via standard `User-Agent` headers.

---

## 2. Component Diagram

```
 +---------------------------------------------------------+
 |                      apis/ Directory                    |
 |            (YAML-based declarative definitions)         |
 +----------------------------+----------------------------+
                              |
                              v
 +---------------------------------------------------------+
 |                     apivitals.loader                    |
 |          (Pydantic v2 Schema Parsing & Validation)      |
 +----------------------------+----------------------------+
                              |
                              v
 +---------------------------------------------------------+
 |                     apivitals.prober                    |
 |     (Async HTTPX probes, SSL inspection, CORS detection)|
 +----------------------------+----------------------------+
                              |
        +---------------------+---------------------+
        |                                           |
        v                                           v
 +-----------------------------+     +-----------------------------+
 |      apivitals.storage      |     |       apivitals.digest      |
 |  - data/catalog.json        |     |  - STATUS.md (live table)   |
 |  - data/status.json         |     |  - reports/digest-YYYY-W*.md|
 |  - data/history.json (30d)  |     |  - README stats updater     |
 |  - data/catalog.csv         |     +-----------------------------+
 |  - data/catalog.db (SQLite) |
 +-----------------------------+
        |
        v
 +-----------------------------+
 |   apivitals.site_generator  |
 |  - site/index.html          |
 |  - site/style.css           |
 |  - site/app.js              |
 |  - GitHub Pages Deployment  |
 +-----------------------------+
```

---

## 3. Data Schemas

### `ApiDefinition` (Pydantic Model)
Located in `apivitals/models.py`:
- `id`: Unique kebab-case slug (e.g., `open-meteo`).
- `name`: Display name.
- `description`: Plain-text explanation of purpose.
- `category`: Functional grouping.
- `homepage`: Website or organization URL.
- `documentation`: Official API documentation URL.
- `auth`: `none`, `api_key`, or `oauth2`.
- `https`: Boolean flag.
- `cors`: Boolean flag.
- `endpoints`: Array of `ApiEndpoint` objects containing `path`, `method`, `expected_status`, `expected_content_type`, and headers.
- `tags`: List of classification tags.
- `license`: Open-source or public data license.
- `rate_limit`: Human-readable rate limits.

### `ServiceStatus` (Pydantic Model)
- `state`: `healthy`, `degraded`, `offline`, `unknown`.
- `latency_ms`: Float response time in milliseconds.
- `status_code`: Received HTTP status code.
- `cors_supported`: Detected `access-control-allow-origin` header.
- `ssl_days_remaining`: Integer days until SSL expiration.
- `uptime_7d_percent` / `uptime_30d_percent`: Calculated rolling uptime percentages.
- `current_streak_days`: Consecutive days healthy.

---

## 4. Synthetic Probing Engine

The prober executes asynchronously using Python's `httpx.AsyncClient` with bounded concurrency (`asyncio.Semaphore(10)`):
- **Latency Timing**: Measures round-trip time with microsecond precision using `time.perf_counter()`.
- **CORS Preflight Detection**: Sends simulated cross-origin origin headers (`Origin: https://apivitals.dev`) and verifies response headers for `Access-Control-Allow-Origin`.
- **SSL Certificate Extraction**: Reads remote TLS certificates over a non-blocking TCP socket to calculate expiration dates.
- **Fail-Safe Aggregation**: Upstream network failures are recorded as status measurements rather than unhandled workflow exceptions.

---

## 5. Storage Layer

Datasets are regenerated atomically:
1. `data/catalog.json`: Serialized catalog.
2. `data/status.json`: Complete snapshot of current vitals and summary metrics.
3. `data/history.json`: Rolling 30-day timeline of health records.
4. `data/catalog.csv`: Tabular export for data analysis.
5. `data/catalog.db`: SQLite relational database indexed by `api_id`.
