"""Static website generator for the ApiVitals web dashboard on GitHub Pages."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from apivitals.models import ApiCatalog, NetworkVitalsSummary

INDEX_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ApiVitals — The Living Health Radar for Free Public APIs</title>
  <meta name="description" content="Continuously audited directory, latency benchmarks, and uptime tracking for free public developer APIs.">
  <link rel="icon" type="image/svg+xml" href="assets/logo.svg">
  <link rel="stylesheet" href="style.css">
</head>
<body data-theme="dark">
  <header class="navbar">
    <div class="nav-container">
      <div class="brand">
        <img src="assets/logo.svg" alt="ApiVitals Logo" class="brand-logo" width="36" height="36">
        <div class="brand-text">
          <span class="brand-title">ApiVitals</span>
          <span class="brand-tag">v0.1.0</span>
        </div>
      </div>
      <div class="nav-actions">
        <a href="https://github.com/apivitals/apivitals" target="_blank" rel="noopener noreferrer" class="nav-link">GitHub</a>
        <a href="data/catalog.json" download class="btn btn-outline">Export JSON</a>
        <button id="themeToggle" class="btn btn-icon" aria-label="Toggle Dark/Light Mode">
          <span id="themeIcon">☀️</span>
        </button>
      </div>
    </div>
  </header>

  <main class="main-content">
    <section class="hero">
      <div class="hero-badge">⚡ Automated Daily Health Probes</div>
      <h1 class="hero-title">The Living Health Radar for Free Public APIs</h1>
      <p class="hero-subtitle">
        Never build against a dead endpoint again. Real-time response latency, verified CORS support, and 30-day uptime metrics for developer-ready public APIs.
      </p>

      <div class="vitals-grid" id="vitalsGrid">
        <div class="vital-card">
          <span class="vital-value" id="statTotal">--</span>
          <span class="vital-label">Monitored APIs</span>
        </div>
        <div class="vital-card">
          <span class="vital-value text-green" id="statUptime">--%</span>
          <span class="vital-label">Global Uptime</span>
        </div>
        <div class="vital-card">
          <span class="vital-value text-blue" id="statAvgLatency">-- ms</span>
          <span class="vital-label">Avg Response</span>
        </div>
        <div class="vital-card">
          <span class="vital-value text-purple" id="statP95">-- ms</span>
          <span class="vital-label">P95 Latency</span>
        </div>
      </div>
    </section>

    <section class="controls-section">
      <div class="search-bar">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" placeholder="Search APIs by name, category, keyword, or endpoint..." aria-label="Search APIs">
        <button id="clearSearch" class="clear-btn" style="display: none;" aria-label="Clear Search">&times;</button>
      </div>

      <div class="filters-row">
        <div class="category-pills" id="categoryPills">
          <button class="pill active" data-category="all">All Categories</button>
        </div>

        <div class="toggle-filters">
          <label class="toggle-label">
            <input type="checkbox" id="corsOnlyFilter">
            <span>CORS Enabled Only</span>
          </label>
          <label class="toggle-label">
            <input type="checkbox" id="noAuthOnlyFilter">
            <span>No Auth Required</span>
          </label>
          <label class="toggle-label">
            <input type="checkbox" id="healthyOnlyFilter">
            <span>Healthy Only</span>
          </label>
        </div>
      </div>
    </section>

    <div class="results-header">
      <span id="resultsCount">Showing all APIs</span>
      <span class="verified-at" id="verifiedAt">Updated: Just now</span>
    </div>

    <section class="api-grid" id="apiGrid">
      <!-- Dynamically populated by app.js -->
    </section>

    <div class="empty-state" id="emptyState" style="display: none;">
      <div class="empty-icon">📡</div>
      <h3>No matching APIs found</h3>
      <p>Try adjusting your search query or disabling active filters.</p>
    </div>
  </main>

  <footer class="footer">
    <div class="footer-container">
      <p>ApiVitals is 100% free and open source under the MIT License.</p>
      <p>Data refreshed daily via GitHub Actions. <a href="https://github.com/apivitals/apivitals" target="_blank">Contribute an API</a> on GitHub.</p>
    </div>
  </footer>

  <!-- Embedded fallback data for offline / file:// usage -->
  <script id="embeddedData" type="application/json">
    DATA_PAYLOAD_PLACEHOLDER
  </script>
  <script src="app.js"></script>
</body>
</html>
"""

STYLE_CSS = """/* ApiVitals Theme & Layout */
:root {
  --bg-primary: #0b0f17;
  --bg-secondary: #131b2a;
  --bg-card: #182337;
  --bg-card-hover: #1f2d47;
  --border-color: #24344d;
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --accent-cyan: #38bdf8;
  --accent-emerald: #10b981;
  --accent-amber: #f59e0b;
  --accent-rose: #f43f5e;
  --accent-purple: #a855f7;
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
}

[data-theme="light"] {
  --bg-primary: #f8fafc;
  --bg-secondary: #ffffff;
  --bg-card: #ffffff;
  --bg-card-hover: #f1f5f9;
  --border-color: #e2e8f0;
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #94a3b8;
  --accent-cyan: #0284c7;
  --accent-emerald: #059669;
  --accent-amber: #d97706;
  --accent-rose: #e11d48;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: var(--font-sans);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.5;
  transition: background-color 0.2s ease, color 0.2s ease;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  border-bottom: 1px solid var(--border-color);
  background-color: var(--bg-secondary);
  position: sticky;
  top: 0;
  z-index: 50;
  backdrop-filter: blur(8px);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.brand-title {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.brand-tag {
  font-size: 0.75rem;
  background-color: var(--border-color);
  color: var(--accent-cyan);
  padding: 0.15rem 0.45rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
  margin-left: 0.25rem;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.nav-link:hover {
  color: var(--text-primary);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.45rem 0.9rem;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
  text-decoration: none;
}

.btn-outline {
  border-color: var(--border-color);
  background-color: transparent;
  color: var(--text-primary);
}

.btn-outline:hover {
  background-color: var(--bg-card-hover);
  border-color: var(--accent-cyan);
}

.btn-icon {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  font-size: 1rem;
}

.btn-icon:hover {
  background-color: var(--bg-card-hover);
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem;
  flex: 1;
  width: 100%;
}

.hero {
  text-align: center;
  margin-bottom: 3rem;
}

.hero-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: rgba(56, 189, 248, 0.1);
  color: var(--accent-cyan);
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.hero-title {
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, var(--text-primary), var(--text-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 1.125rem;
  color: var(--text-secondary);
  max-width: 700px;
  margin: 0 auto 2.5rem auto;
}

.vitals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  max-width: 900px;
  margin: 0 auto;
}

.vital-card {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  text-align: center;
}

.vital-value {
  display: block;
  font-size: 1.75rem;
  font-weight: 800;
  margin-bottom: 0.25rem;
}

.vital-label {
  font-size: 0.825rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}

.text-green { color: var(--accent-emerald); }
.text-blue { color: var(--accent-cyan); }
.text-purple { color: var(--accent-purple); }

.controls-section {
  margin-bottom: 2rem;
}

.search-bar {
  position: relative;
  margin-bottom: 1.25rem;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.search-bar input {
  width: 100%;
  padding: 0.85rem 2.8rem 0.85rem 2.8rem;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s;
}

.search-bar input:focus {
  border-color: var(--accent-cyan);
}

.clear-btn {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.25rem;
  cursor: pointer;
}

.filters-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.category-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.pill {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 0.35rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.pill:hover {
  border-color: var(--accent-cyan);
  color: var(--text-primary);
}

.pill.active {
  background-color: var(--accent-cyan);
  border-color: var(--accent-cyan);
  color: #0b0f17;
  font-weight: 700;
}

.toggle-filters {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
  cursor: pointer;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 1.25rem;
  padding: 0 0.25rem;
}

.api-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1.5rem;
}

.api-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
}

.api-card:hover {
  transform: translateY(-2px);
  border-color: var(--accent-cyan);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  gap: 0.5rem;
}

.card-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.badge-healthy { background: rgba(16, 185, 129, 0.15); color: var(--accent-emerald); }
.badge-degraded { background: rgba(245, 158, 11, 0.15); color: var(--accent-amber); }
.badge-offline { background: rgba(244, 63, 94, 0.15); color: var(--accent-rose); }

.card-category {
  display: inline-block;
  font-size: 0.75rem;
  color: var(--accent-cyan);
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.card-description {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
  flex: 1;
}

.card-vitals {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 0.6rem;
  margin-bottom: 1rem;
  text-align: center;
}

.vital-metric {
  display: flex;
  flex-direction: column;
}

.vital-metric-val {
  font-size: 0.9rem;
  font-weight: 700;
}

.vital-metric-lbl {
  font-size: 0.7rem;
  color: var(--text-muted);
  text-transform: uppercase;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 1rem;
}

.tag-badge {
  background-color: var(--border-color);
  color: var(--text-secondary);
  font-size: 0.7rem;
  padding: 0.15rem 0.4rem;
  border-radius: var(--radius-sm);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border-color);
  padding-top: 1rem;
  font-size: 0.85rem;
}

.card-links {
  display: flex;
  gap: 0.75rem;
}

.card-links a {
  color: var(--accent-cyan);
  text-decoration: none;
  font-weight: 600;
}

.card-links a:hover {
  text-decoration: underline;
}

.empty-state {
  text-align: center;
  padding: 4rem 1rem;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.footer {
  border-top: 1px solid var(--border-color);
  background-color: var(--bg-secondary);
  padding: 2rem 1.5rem;
  text-align: center;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.footer a {
  color: var(--accent-cyan);
  text-decoration: none;
}

@media (max-width: 768px) {
  .api-grid {
    grid-template-columns: 1fr;
  }
  .filters-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
"""

APP_JS = """// ApiVitals Client-side Interactive Dashboard
(function () {
  let allApis = [];
  let statusMap = {};
  let currentCategory = 'all';

  // DOM Elements
  const apiGrid = document.getElementById('apiGrid');
  const searchInput = document.getElementById('searchInput');
  const clearSearch = document.getElementById('clearSearch');
  const categoryPills = document.getElementById('categoryPills');
  const corsOnlyFilter = document.getElementById('corsOnlyFilter');
  const noAuthOnlyFilter = document.getElementById('noAuthOnlyFilter');
  const healthyOnlyFilter = document.getElementById('healthyOnlyFilter');
  const resultsCount = document.getElementById('resultsCount');
  const emptyState = document.getElementById('emptyState');
  const verifiedAt = document.getElementById('verifiedAt');
  const themeToggle = document.getElementById('themeToggle');
  const themeIcon = document.getElementById('themeIcon');

  // Stats DOM
  const statTotal = document.getElementById('statTotal');
  const statUptime = document.getElementById('statUptime');
  const statAvgLatency = document.getElementById('statAvgLatency');
  const statP95 = document.getElementById('statP95');

  // Theme Management
  function initTheme() {
    const savedTheme = localStorage.getItem('apivitals_theme') || 'dark';
    document.body.setAttribute('data-theme', savedTheme);
    themeIcon.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
  }

  themeToggle.addEventListener('click', () => {
    const current = document.body.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.body.setAttribute('data-theme', next);
    localStorage.setItem('apivitals_theme', next);
    themeIcon.textContent = next === 'dark' ? '☀️' : '🌙';
  });

  // Load Data: try fetch first, fallback to embedded JSON
  async function loadData() {
    try {
      const [catRes, statRes] = await Promise.all([
        fetch('data/catalog.json'),
        fetch('data/status.json')
      ]);
      if (catRes.ok && statRes.ok) {
        const catalog = await catRes.json();
        const status = await statRes.json();
        setupDashboard(catalog, status);
        return;
      }
    } catch (e) {
      console.warn('Network fetch failed, reading embedded payload...', e);
    }

    // Fallback
    const fallbackScript = document.getElementById('embeddedData');
    if (fallbackScript && fallbackScript.textContent.trim()) {
      try {
        const payload = JSON.parse(fallbackScript.textContent);
        setupDashboard(payload.catalog, payload.status);
      } catch (err) {
        console.error('Failed to parse embedded data:', err);
      }
    }
  }

  function setupDashboard(catalog, status) {
    allApis = catalog.apis || [];
    statusMap = {};
    if (status && status.services) {
      status.services.forEach(s => { statusMap[s.api_id] = s; });
    }

    // Update Global Stats
    if (status) {
      statTotal.textContent = status.total_monitored || allApis.length;
      statUptime.textContent = `${status.overall_uptime_pct || 100}%`;
      statAvgLatency.textContent = `${status.avg_latency_ms || 0} ms`;
      statP95.textContent = `${status.p95_latency_ms || 0} ms`;
      if (status.generated_at) {
        verifiedAt.textContent = `Updated: ${new Date(status.generated_at).toLocaleString()}`;
      }
    }

    // Build Categories
    const categories = catalog.categories || [];
    categories.forEach(cat => {
      const btn = document.createElement('button');
      btn.className = 'pill';
      btn.dataset.category = cat;
      btn.textContent = cat;
      categoryPills.appendChild(btn);
    });

    renderApis();
  }

  function renderApis() {
    const query = searchInput.value.toLowerCase().trim();
    const corsOnly = corsOnlyFilter.checked;
    const noAuthOnly = noAuthOnlyFilter.checked;
    const healthyOnly = healthyOnlyFilter.checked;

    const filtered = allApis.filter(api => {
      const st = statusMap[api.id] || { state: 'healthy', latency_ms: 0, uptime_7d_percent: 100, cors_supported: api.cors };

      // Category filter
      if (currentCategory !== 'all' && api.category !== currentCategory) return false;

      // CORS filter
      if (corsOnly && !st.cors_supported && !api.cors) return false;

      // Auth filter
      if (noAuthOnly && api.auth !== 'none') return false;

      // Healthy filter
      if (healthyOnly && st.state !== 'healthy') return false;

      // Search Query
      if (query) {
        const matchName = api.name.toLowerCase().includes(query);
        const matchDesc = api.description.toLowerCase().includes(query);
        const matchCategory = api.category.toLowerCase().includes(query);
        const matchTags = (api.tags || []).some(t => t.toLowerCase().includes(query));
        const matchEndpoints = (api.endpoints || []).some(ep => ep.path.toLowerCase().includes(query));
        if (!matchName && !matchDesc && !matchCategory && !matchTags && !matchEndpoints) {
          return false;
        }
      }

      return true;
    });

    resultsCount.textContent = `Showing ${filtered.length} of ${allApis.length} APIs`;

    if (filtered.length === 0) {
      apiGrid.innerHTML = '';
      emptyState.style.display = 'block';
      return;
    }

    emptyState.style.display = 'none';
    apiGrid.innerHTML = filtered.map(api => {
      const st = statusMap[api.id] || { state: 'healthy', latency_ms: 120, uptime_7d_percent: 100, cors_supported: api.cors, ssl_days_remaining: 180 };
      const badgeClass = st.state === 'healthy' ? 'badge-healthy' : (st.state === 'degraded' ? 'badge-degraded' : 'badge-offline');
      const badgeText = st.state.charAt(0).toUpperCase() + st.state.slice(1);
      const latencyText = st.latency_ms > 0 ? `${st.latency_ms} ms` : 'N/A';
      const corsText = (st.cors_supported || api.cors) ? '✅ CORS' : '❌ No CORS';
      const authLabel = api.auth === 'none' ? '🔑 No Key' : (api.auth === 'api_key' ? '🔐 API Key' : '🔒 OAuth');
      const tagsHtml = (api.tags || []).map(t => `<span class="tag-badge">#${t}</span>`).join('');
      const sampleEndpoint = api.endpoints && api.endpoints.length > 0 ? api.endpoints[0].path : api.homepage;

      return `
        <article class="api-card">
          <div>
            <div class="card-header">
              <h3 class="card-title">${escapeHtml(api.name)}</h3>
              <span class="status-badge ${badgeClass}">${badgeText}</span>
            </div>
            <span class="card-category">${escapeHtml(api.category)}</span>
            <p class="card-description">${escapeHtml(api.description)}</p>

            <div class="card-vitals">
              <div class="vital-metric">
                <span class="vital-metric-val text-blue">${latencyText}</span>
                <span class="vital-metric-lbl">Latency</span>
              </div>
              <div class="vital-metric">
                <span class="vital-metric-val text-green">${st.uptime_7d_percent || 100}%</span>
                <span class="vital-metric-lbl">7d Uptime</span>
              </div>
              <div class="vital-metric">
                <span class="vital-metric-val">${corsText}</span>
                <span class="vital-metric-lbl">CORS</span>
              </div>
            </div>

            <div class="card-tags">
              <span class="tag-badge">${authLabel}</span>
              ${tagsHtml}
            </div>
          </div>

          <footer class="card-footer">
            <span style="font-size: 0.75rem; color: var(--text-muted);">${escapeHtml(api.rate_limit || 'Free Tier')}</span>
            <div class="card-links">
              <a href="${escapeHtml(api.documentation)}" target="_blank" rel="noopener noreferrer">Docs &rarr;</a>
              <a href="${escapeHtml(api.homepage)}" target="_blank" rel="noopener noreferrer">Home</a>
            </div>
          </footer>
        </article>
      `;
    }).join('');
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  // Event Listeners
  categoryPills.addEventListener('click', (e) => {
    if (e.target.classList.contains('pill')) {
      categoryPills.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
      e.target.classList.add('active');
      currentCategory = e.target.dataset.category;
      renderApis();
    }
  });

  searchInput.addEventListener('input', () => {
    clearSearch.style.display = searchInput.value ? 'block' : 'none';
    renderApis();
  });

  clearSearch.addEventListener('click', () => {
    searchInput.value = '';
    clearSearch.style.display = 'none';
    renderApis();
  });

  corsOnlyFilter.addEventListener('change', renderApis);
  noAuthOnlyFilter.addEventListener('change', renderApis);
  healthyOnlyFilter.addEventListener('change', renderApis);

  // Initialize
  initTheme();
  loadData();
})();
"""


def build_site(
    catalog: ApiCatalog,
    summary: NetworkVitalsSummary,
    output_dir: str | Path = "site",
    assets_dir: str | Path = "assets",
    data_dir: str | Path = "data",
) -> None:
    """Generate complete static website inside output_dir."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Embed data for offline/standalone reliability
    payload = {
        "catalog": catalog.model_dump(mode="json"),
        "status": summary.model_dump(mode="json"),
    }
    html_content = INDEX_HTML_TEMPLATE.replace("DATA_PAYLOAD_PLACEHOLDER", json.dumps(payload))

    (out / "index.html").write_text(html_content, encoding="utf-8")
    (out / "style.css").write_text(STYLE_CSS, encoding="utf-8")
    (out / "app.js").write_text(APP_JS, encoding="utf-8")

    # Copy assets (logo, banner) into site/assets
    site_assets = out / "assets"
    site_assets.mkdir(parents=True, exist_ok=True)
    src_assets = Path(assets_dir)
    if src_assets.is_dir():
        for f in src_assets.glob("*.svg"):
            shutil.copy2(f, site_assets / f.name)

    # Copy data JSONs into site/data for static fetch
    site_data = out / "data"
    site_data.mkdir(parents=True, exist_ok=True)
    src_data = Path(data_dir)
    if src_data.is_dir():
        for f in src_data.glob("*.json"):
            shutil.copy2(f, site_data / f.name)
        for f in src_data.glob("*.csv"):
            shutil.copy2(f, site_data / f.name)
