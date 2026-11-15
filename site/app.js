// ApiVitals Client-side Interactive Dashboard
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
