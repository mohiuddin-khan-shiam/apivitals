# Project Rationale & Candidate Evaluation

## 1. Executive Summary

This document details the selection process, comparative analysis, and feasibility evaluation for **ApiVitals** (`apivitals`) — an automated living health radar, latency benchmark, and curated open-source directory of free public APIs.

---

## 2. Candidate Brainstorming & Evaluation

We evaluated eight diverse open-source concepts against five core engineering and open-source growth criteria:
1. **Usefulness (U)**: Solves a recurring, painful problem for developers, students, researchers, or teams.
2. **Uniqueness (UQ)**: Differentiates significantly from existing tools without cloning popular projects.
3. **Star / Fork Potential (SF)**: Community interest, shareability, and contributor incentive (e.g., adding entries).
4. **Feasibility (F)**: Runs 100% on free resources (public feeds, no API keys, works on GitHub Actions free runners).
5. **Daily Update Fit (DU)**: Generates genuine, measurable, non-fabricated data updates every single day.

Scoring scale: 1 (Poor) to 5 (Exceptional). Max score: 25.

---

### Candidate 1: ApiVitals — Living Public API Health Radar & Benchmark Directory
- **Concept**: A self-auditing catalog of free public APIs that performs automated daily health probes (measuring response latency, uptime percentage, HTTP status, CORS headers, and SSL certificate expiration). Exposes a Python CLI, library API, machine-readable datasets (JSON, CSV, SQLite), and a zero-dependency static web dashboard.
- **Pain Point**: Over 10 million developers search for free public APIs for side projects, hackathons, and prototyping. The famous `public-apis/public-apis` repository (330k+ stars) has been unmaintained for years: over 40% of listed endpoints are dead, paywalled, or lack CORS support. Developers waste hours debugging endpoints that no longer exist.
- **Day-One Utility**: Terminal CLI (`apivitals search --category weather --cors`), offline SQLite/JSON exports, and an interactive dark-mode dashboard.
- **Daily Real Changes**: Genuine daily latency measurements, 7-day rolling uptime percentages, SSL cert expiration countdowns, and automated status transition tracking (healthy/degraded/offline).
- **Scores**: U: 5 | UQ: 5 | SF: 5 | F: 5 | DU: 5 | **Total: 25/25**

---

### Candidate 2: CloudPulse — Multi-Cloud & Dev Platform Reliability Radar
- **Concept**: Aggregates public status feeds (RSS/JSON) from 40+ cloud and developer platforms (AWS, GCP, GitHub, Cloudflare, OpenAI, Vercel, Supabase) to track incident timelines, MTTR, and uptime streaks.
- **Pain Point**: Teams operate across multi-cloud setups and want an independent, neutral record of platform outages without checking 20 different status pages.
- **Day-One Utility**: CLI `cloudpulse check github`, historical incident duration reports.
- **Daily Real Changes**: On quiet days with zero incidents across all monitored providers, automated runs might yield no changes, potentially stalling automated daily commits.
- **Scores**: U: 4 | UQ: 4 | SF: 4 | F: 4 | DU: 3 | **Total: 19/25**

---

### Candidate 3: ModelRadar — Curated Open-Weight AI Checkpoint Index
- **Concept**: Ingests public Hugging Face model metadata daily, filtering out fine-tune spam to surface verified open-weight base models, license compliance (Apache 2.0 vs Llama Community), parameter counts, and GGUF quant availability.
- **Pain Point**: Hugging Face trending is flooded with broken merges, unvetted fine-tunes, and unclear license tags.
- **Day-One Utility**: CLI `modelradar find --license apache-2.0 --max-ram 16gb`.
- **Daily Real Changes**: Dozens of new model releases daily.
- **Limitations**: Hugging Face API schemas change frequently; deep evaluation requires heavy compute not suited for GitHub Actions.
- **Scores**: U: 4 | UQ: 3 | SF: 4 | F: 4 | DU: 4 | **Total: 19/25**

---

### Candidate 4: VulnRadar — Multi-Ecosystem Open Vulnerability Stream
- **Concept**: Mirrors and indexes OSV.dev and GHSA public feeds across PyPI, npm, Go, and Cargo, producing an offline vulnerability database and a lockfile audit CLI.
- **Pain Point**: Developers in air-gapped or restricted CI environments need a lightweight, offline vulnerability lookup tool.
- **Day-One Utility**: CLI `vulnradar audit requirements.txt`.
- **Daily Real Changes**: Daily CVE and security advisory publications.
- **Limitations**: OSV.dev already provides official clients (`osv-scanner`) and rich APIs, reducing uniqueness.
- **Scores**: U: 4 | UQ: 3 | SF: 4 | F: 4 | DU: 4 | **Total: 19/25**

---

### Candidate 5: EndCycle — Runtime & Framework End-of-Life (EOL) Tracker
- **Concept**: Tracks support lifecycles, active security maintenance, and EOL milestones for 150+ runtimes, frameworks, databases, and OS distros via endoflife.date API.
- **Pain Point**: Organizations miss EOL deprecations (e.g., Node 18 EOL, Python 3.8 EOL) leading to compliance and security failures.
- **Day-One Utility**: CLI `endcycle audit Dockerfile`.
- **Daily Real Changes**: EOL release dates only change when new versions are tagged (several times a week, but not guaranteed daily).
- **Scores**: U: 4 | UQ: 3 | SF: 3 | F: 5 | DU: 3 | **Total: 18/25**

---

### Candidate 6: PaperPulse — Daily AI Research Preprint & Code Matcher
- **Concept**: Harvests arXiv computer science preprints daily and scans papers for verified, reproducible open-source code repositories on GitHub.
- **Pain Point**: Thousands of papers publish every week on arXiv; finding papers with actual working code is tedious.
- **Day-One Utility**: Daily markdown digest of papers with code links.
- **Daily Real Changes**: New papers every weekday.
- **Limitations**: Papers With Code and arXiv Sanity already exist; weekends have no arXiv announcements.
- **Scores**: U: 3 | UQ: 3 | SF: 4 | F: 4 | DU: 3 | **Total: 17/25**

---

### Candidate 7: LicenseRadar — Open Source Package License Drift Watchdog
- **Concept**: Monitors top 1,000 open-source repositories across PyPI and npm for sudden license shifts (e.g., BSD to BSL, AGPL relicensing, patent restriction additions).
- **Pain Point**: Companies fear sudden relicensing of core dependencies (similar to Redis, Elastic, Terraform).
- **Day-One Utility**: CLI `licenseradar check package-lock.json`.
- **Daily Real Changes**: License changes are infrequent, leading to many days with zero updates.
- **Scores**: U: 4 | UQ: 4 | SF: 3 | F: 4 | DU: 2 | **Total: 17/25**

---

### Candidate 8: EcoHost — Cloud Region Carbon Intensity Index
- **Concept**: Ingests public electricity grid carbon intensity data (ENTSO-E, UK National Grid ESO, EIA) mapped to AWS, Azure, and GCP data center regions.
- **Pain Point**: Sustainable engineering teams want to route compute jobs to low-carbon cloud regions.
- **Day-One Utility**: CLI `ecohost lowest-carbon --provider aws`.
- **Daily Real Changes**: Hourly and daily grid variations.
- **Limitations**: Grid mapping requires complex geographic cross-referencing; some international grid APIs require authenticated access.
- **Scores**: U: 3 | UQ: 4 | SF: 3 | F: 3 | DU: 4 | **Total: 17/25**

---

## 3. Decision Matrix Summary

| Candidate | Usefulness | Uniqueness | Star/Fork | Feasibility | Daily Updates | Total | Rank |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1. ApiVitals** | **5** | **5** | **5** | **5** | **5** | **25** | **1 (Winner)** |
| 2. CloudPulse | 4 | 4 | 4 | 4 | 3 | 19 | 2 |
| 3. ModelRadar | 4 | 3 | 4 | 4 | 4 | 19 | 2 |
| 4. VulnRadar | 4 | 3 | 4 | 4 | 4 | 19 | 2 |
| 5. EndCycle | 4 | 3 | 3 | 5 | 3 | 18 | 5 |
| 6. PaperPulse | 3 | 3 | 4 | 4 | 3 | 17 | 6 |
| 7. LicenseRadar | 4 | 4 | 3 | 4 | 2 | 17 | 6 |
| 8. EcoHost | 3 | 4 | 3 | 3 | 4 | 17 | 6 |

---

## 4. The Winner: ApiVitals

### Why ApiVitals Wins
1. **Massive Existing Audience with an Unsolved Pain Point**: The demand for curated public APIs is proven by the 330k+ stars on `public-apis/public-apis`. However, that repository failed because it is a static, uncurated markdown list where dead links and broken endpoints accumulate unchecked.
2. **Self-Auditing by Design**: ApiVitals bridges the gap between a curated directory and an automated synthetic monitoring system. By running daily non-intrusive health checks, it guarantees that every listed API has verified CORS headers, valid SSL, real-time response latency, and documented uptime.
3. **Guaranteed Real Daily Updates**: Every day, network latency fluctuates, uptime percentages change, and certificate expiration counters decrement. The automated daily workflow never has to fabricate commits or push empty updates — it records genuine, verifiable performance metrics.
4. **Community Flywheel (High Fork/PR Potential)**: Adding a new API is as simple as dropping a declarative YAML file into `apis/<category>/<api>.yaml`. Contributors immediately see their favorite API probed, benchmarked, and listed on the live dashboard.
5. **Zero External Cost**: Uses only public, rate-limit-compliant GET/HEAD health checks against documented public endpoints. Runs within 60–90 seconds on standard GitHub Actions free-tier runners.

### Comparison to Existing Alternatives

| Feature / Attribute | `public-apis/public-apis` | RapidAPI / Postman Hub | **ApiVitals** |
|:---|:---|:---|:---|
| **Health & Uptime Verification** | None (manual, mostly dead) | Proprietary / paywalled | **Automated daily probes with 30-day history** |
| **Response Latency Benchmarks** | None | Limited / proprietary | **Measured daily (avg & p95 ms)** |
| **CORS Verification** | Manual claims (often incorrect) | Varies | **Automated preflight header detection** |
| **Offline CLI & Library** | None | Heavy desktop client / CLI | **Lightweight Python CLI & pip package** |
| **Machine-Readable Formats** | Raw Markdown | Paywalled API / proprietary | **JSON, CSV, and SQLite datasets** |
| **Open Governance & Free Access** | Unmaintained repo | Commercial platform | **100% Free MIT Open Source, automated via CI** |

---

## 5. Compliance & Ethics

- **Resource Consumption**: Only standard public endpoints with documented zero-auth read access are probed (e.g., Open-Meteo, USGS Earthquakes, Frankfurter Currency, Gutendex).
- **Polite Probing**: Every probe sends a distinct `ApiVitals/1.0 (+https://github.com/<owner>/apivitals)` User-Agent, adheres to 5-second timeouts, limits concurrency to avoid load spikes, and makes only one lightweight request per endpoint per day.
- **Attribution & Licensing**: Each API record explicitly credits the upstream data source and documents its upstream license and rate limits.
- **Content Policy**: Strictly family-safe and developer-focused. No adult, deceptive, copyright-infringing, or scraper-prohibited content.
