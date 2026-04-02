import { api } from '../api.js'

let state = {
  metric: 'xp',
  page: 1,
  limit: 10,
  total: 0,
  loading: false,
}

export function leaderboardPage() {
  const el = document.createElement('div')
  el.className = 'page'
  el.innerHTML = `
    <div class="page-header">
      <div class="page-eyebrow">Rankings</div>
      <h1 class="page-title">Leaderboard</h1>
      <p class="page-sub">See who's grinding the hardest. Updated every minute.</p>
    </div>

    <div class="glass-card">
      <div class="toolbar">
        <span class="toolbar-label">Sort by</span>
        <div class="pill-group" id="metricPills">
          <button class="pill active" data-metric="xp">⚡ XP</button>
          <button class="pill" data-metric="rating">📈 Rating</button>
        </div>

        <span class="toolbar-label" style="margin-left:auto">Rows</span>
        <select class="select-styled" id="limitSel">
          <option value="10">10</option>
          <option value="25">25</option>
          <option value="50">50</option>
        </select>

        <button class="btn-action" id="reloadBtn">Apply</button>
      </div>

      <div id="tableWrap">
        ${skeletonRows()}
      </div>

      <div class="pagination">
        <span class="page-info" id="pageInfo">Loading…</span>
        <div class="page-controls">
          <button class="btn-secondary" id="prevBtn" disabled>← Prev</button>
          <button class="btn-secondary" id="nextBtn" disabled>Next →</button>
        </div>
      </div>
    </div>
  `

  // Wire controls
  el.querySelectorAll('[data-metric]').forEach(btn => {
    btn.addEventListener('click', () => {
      el.querySelectorAll('[data-metric]').forEach(b => b.classList.remove('active'))
      btn.classList.add('active')
      state.metric = btn.dataset.metric
      state.page = 1
      load(el)
    })
  })

  el.querySelector('#limitSel').addEventListener('change', e => {
    state.limit = parseInt(e.target.value)
    state.page = 1
    load(el)
  })

  el.querySelector('#reloadBtn').addEventListener('click', () => {
    state.page = 1
    load(el)
  })

  el.querySelector('#prevBtn').addEventListener('click', () => {
    if (state.page > 1) { state.page--; load(el) }
  })

  el.querySelector('#nextBtn').addEventListener('click', () => {
    const maxPage = Math.ceil(state.total / state.limit)
    if (state.page < maxPage) { state.page++; load(el) }
  })

  // Initial load
  load(el)
  return el
}

async function load(el) {
  if (state.loading) return
  state.loading = true

  const wrap = el.querySelector('#tableWrap')
  const prevBtn = el.querySelector('#prevBtn')
  const nextBtn = el.querySelector('#nextBtn')
  const pageInfo = el.querySelector('#pageInfo')

  wrap.innerHTML = skeletonRows()
  prevBtn.disabled = true
  nextBtn.disabled = true
  pageInfo.textContent = 'Loading…'

  try {
    const data = await api.leaderboard(state.metric, state.page, state.limit)
    state.total = data.total
    const maxPage = Math.ceil(state.total / state.limit)

    if (!data.entries || data.entries.length === 0) {
      wrap.innerHTML = `
        <div class="state-msg">
          <span class="state-icon">📭</span>
          <span class="state-text">No entries on page ${state.page}</span>
        </div>`
    } else {
      wrap.innerHTML = renderTable(data.entries, state.metric)
      // Stagger row animations
      wrap.querySelectorAll('tbody tr').forEach((tr, i) => {
        tr.style.animationDelay = `${i * 35}ms`
      })
    }

    pageInfo.textContent = `Page ${state.page} of ${maxPage} — ${data.total} users`
    prevBtn.disabled = state.page <= 1
    nextBtn.disabled = state.page >= maxPage
  } catch (err) {
    wrap.innerHTML = `
      <div class="state-msg">
        <span class="state-icon">⚠️</span>
        <span class="state-text">Failed to load: ${err.message}</span>
      </div>`
    pageInfo.textContent = 'Error'
  } finally {
    state.loading = false
  }
}

function renderTable(entries, metric) {
  const rows = entries.map(row => {
    const rankClass = row.rank === 1 ? 'rank-1' : row.rank === 2 ? 'rank-2' : row.rank === 3 ? 'rank-3' : 'rank-other'
    const initial = (row.cf_handle || '?')[0].toUpperCase()
    const highlighted = metric === 'xp'
      ? `<td class="xp-value">${row.xp.toLocaleString()}</td><td class="rating-value" style="opacity:0.5">${row.rating.toLocaleString()}</td>`
      : `<td class="xp-value" style="opacity:0.5">${row.xp.toLocaleString()}</td><td class="rating-value">${row.rating.toLocaleString()}</td>`

    return `
      <tr>
        <td><span class="rank-badge ${rankClass}">${row.rank}</span></td>
        <td>
          <div class="handle-cell">
            <div class="handle-avatar">${initial}</div>
            <div>
              <div class="handle-name">${escHtml(row.cf_handle)}</div>
              <div style="font-size:0.72rem;color:var(--text-muted)">Discord: ${escHtml(row.discord_id)}</div>
            </div>
          </div>
        </td>
        ${highlighted}
        <td><span class="level-badge">Lv ${row.level}</span></td>
      </tr>`
  }).join('')

  return `
    <table class="lb-table">
      <thead>
        <tr>
          <th style="width:64px">Rank</th>
          <th>Player</th>
          <th>XP</th>
          <th>Rating</th>
          <th>Level</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>`
}

function skeletonRows() {
  return `<div style="padding:0.5rem 0">${
    Array(8).fill('<div class="skeleton skeleton-row" style="margin:4px 1.5rem;border-radius:8px"></div>').join('')
  }</div>`
}

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
}
