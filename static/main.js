/* ═══════════════════════════════════════════════
   WebMetrics Dashboard — main.js
   Fetches API endpoints and populates the UI
═══════════════════════════════════════════════ */

// ── Utility: format numbers nicely ──
function fmt(val, prefix = '', suffix = '', isDecimal = false) {
  if (val === undefined || val === null) return '—';
  const n = isDecimal
    ? parseFloat(val).toFixed(2)
    : parseInt(val, 10).toLocaleString('en-IN');
  return `${prefix}${n}${suffix}`;
}

// ── Animate counting up for KPI values ──
function animateCount(el, target, prefix, suffix, isDecimal) {
  const duration = 1200;
  const start = performance.now();
  const from = 0;

  function tick(now) {
    const progress = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    const current = from + (target - from) * ease;
    el.textContent = isDecimal
      ? `${prefix}${current.toFixed(2)}${suffix}`
      : `${prefix}${Math.round(current).toLocaleString('en-IN')}${suffix}`;
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

// ── Render KPI cards ──
function renderStats(data) {
  document.querySelectorAll('.kpi-card').forEach(card => {
    const key    = card.dataset.key;
    const prefix = card.dataset.prefix || '';
    const suffix = card.dataset.suffix || '';
    const isDec  = card.dataset.format === 'decimal';
    const el     = card.querySelector('.kpi-value');
    if (el && data[key] !== undefined) {
      animateCount(el, parseFloat(data[key]), prefix, suffix, isDec);
    }
  });

  // Statistics cards
  setEl('stat-mean',   fmt(data.revenue_mean, '$', '', true));
  setEl('stat-median', fmt(data.revenue_median, '$', '', true));
  setEl('stat-mode',   fmt(data.revenue_mode, '$', '', true));
  setEl('stat-shape',  `${data.row_count} × ${data.col_count}`);
}

function setEl(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

// ── Render a chart into a container ──
function renderChart(containerId, b64, isFullWidth = false) {
  const container = document.getElementById(containerId);
  if (!container || !b64) return;

  const img = document.createElement('img');
  img.src = `data:image/png;base64,${b64}`;
  img.alt = containerId;
  img.style.opacity = '0';
  img.style.transition = 'opacity .4s ease';

  if (isFullWidth) {
    container.innerHTML = '';
    container.appendChild(img);
  } else {
    const body = container.querySelector('.chart-body');
    if (body) {
      body.innerHTML = '';
      body.appendChild(img);
    }
  }

  img.onload = () => { img.style.opacity = '1'; };
}

// ── Render EDA table ──
function renderEDA(data) {
  const grid = document.getElementById('eda-grid');
  if (!grid) return;

  const cols = Object.keys(data.describe);
  const stats = ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max'];

  let html = '<table><thead><tr><th>Statistic</th>';
  cols.forEach(c => { html += `<th>${c}</th>`; });
  html += '</tr></thead><tbody>';

  stats.forEach(s => {
    html += `<tr><td>${s}</td>`;
    cols.forEach(c => {
      const val = data.describe[c]?.[s];
      html += `<td>${val !== undefined ? parseFloat(val).toLocaleString('en-IN', {maximumFractionDigits: 2}) : '—'}</td>`;
    });
    html += '</tr>';
  });

  html += '</tbody></table>';
  grid.innerHTML = html;
}

// ── Main: fetch all API endpoints ──
async function init() {
  try {
    // Fetch stats and charts in parallel
    const [statsRes, chartsRes, edaRes] = await Promise.all([
      fetch('/api/stats'),
      fetch('/api/charts'),
      fetch('/api/eda'),
    ]);

    const stats  = await statsRes.json();
    const charts = await chartsRes.json();
    const eda    = await edaRes.json();

    renderStats(stats);

    // Full-width charts
    renderChart('chart-trend',     charts.trend,     true);
    renderChart('chart-heatmap',   charts.heatmap,   true);

    // Grid charts
    renderChart('chart-histogram', charts.histogram);
    renderChart('chart-bar',       charts.bar);
    renderChart('chart-scatter',   charts.scatter);
    renderChart('chart-boxplot',   charts.boxplot);

    renderEDA(eda);

  } catch (err) {
    console.error('Dashboard load error:', err);
  }
}

// ── Activate nav pill on scroll ──
function initScrollSpy() {
  const sections = document.querySelectorAll('section[id]');
  const pills    = document.querySelectorAll('.pill');

  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        pills.forEach(p => p.classList.remove('active'));
        const active = document.querySelector(`.pill[href="#${e.target.id}"]`);
        if (active) active.classList.add('active');
      }
    });
  }, { threshold: 0.4 });

  sections.forEach(s => observer.observe(s));
}

document.addEventListener('DOMContentLoaded', () => {
  init();
  initScrollSpy();
});
