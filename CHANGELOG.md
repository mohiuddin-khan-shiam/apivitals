# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-11-16

### Added
- Initial release of **ApiVitals** — the living health radar and curated directory of free public APIs.
- Curated collection of 20 verified public APIs across 10 categories (Weather, Geocoding, Science, Finance, Developer Tools, Books, Entertainment, Government, Health, Food).
- Core asynchronous and synchronous network probe engine with latency measurement, HTTP status detection, CORS header validation, and SSL expiration calculation.
- Pydantic models for declarative API specifications (`ApiDefinition`, `ApiEndpoint`, `ServiceStatus`, `NetworkVitalsSummary`).
- Command-line interface (`apivitals`) with commands: `validate`, `list`, `search`, `probe`, `stats`, `export`, and `update`.
- Multi-format dataset exporters: `data/catalog.json`, `data/status.json`, `data/history.json`, `data/catalog.csv`, and `data/catalog.db` (SQLite).
- High-performance, zero-dependency static web dashboard with instant client-side fuzzy search, category filter pills, CORS/Auth toggles, and dark/light theme switching.
- Automated GitHub Actions workflows:
  - `daily-update.yml`: Scheduled daily health probes and conventional commit generation.
  - `weekly-digest.yml`: Weekly reliability and performance digest publisher.
  - `maintenance.yml`: Dependency health and README stats synchronization.
  - `ci.yml`: Multi-OS (Ubuntu, macOS, Windows) and multi-Python (3.10-3.13) test matrix.
  - `pages.yml`: Automated GitHub Pages static dashboard deployment.
- Documentation, architecture diagrams, contributing guidelines, and issue templates.
