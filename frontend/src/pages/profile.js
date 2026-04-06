import { api } from '../api.js'
import { Chart, LineController, LineElement, PointElement, LinearScale, TimeScale, CategoryScale, Filler, Tooltip, Legend } from 'chart.js'

Chart.register(LineController, LineElement, PointElement, LinearScale, CategoryScale, TimeScale, Filler, Tooltip, Legend)

let chartInstance = null
const SESSION_DISCORD_ID_KEY = 'botme.session.discordId'

export function myProfilePage() {
  return buildProfilePage('self')
}

export function searchProfilesPage() {
  return buildProfilePage('search')
}

function buildProfilePage(mode) {
  const isSelfPage = mode === 'self'
  const el = document.createElement('div')
  el.className = 'page'
  el.innerHTML = `
    <div class="page-header">
      <div class="page-eyebrow">Stats & Analytics</div>
      <h1 class="page-title">${isSelfPage ? 'Your Profile' : 'Search Profiles'}</h1>
      <p class="page-sub">${isSelfPage
        ? 'Enter your Discord ID below to load your stats. Float saves it locally so you only need to do this once.'
        : 'Enter a Codeforces handle to view another user\'s progress, XP, and rating charts.'}
      </p>
    </div>

    ${isSelfPage ? `
      <div class="profile-auth">
        <input
          class="input-styled"
          id="discordInput"
          placeholder="Discord ID (e.g. 123456789012345678)"
          autocomplete="off"
          spellcheck="false"
        />
        <button class="btn-action" id="saveSessionBtn">Sign In</button>
        <button class="btn-secondary" id="logoutBtn">Clear</button>
      </div>
      <div class="session-hint" id="sessionHint">No active session.</div>
    ` : `
      <div class="profile-search">
        <input
          class="input-styled"
          id="handleInput"
          placeholder="CF handle (e.g. tourist)"
          autocomplete="off"
          spellcheck="false"
        />
        <button class="btn-action" id="loadBtn">Load Profile</button>
      </div>
    `}

    <div id="profileResult" style="display:none">
      <div class="tab-list">
        <button class="tab-btn active" data-platform="codeforces">⚔️ Codeforces</button>
        <button class="tab-btn" data-platform="leetcode">🧩 LeetCode</button>
      </div>

      <div class="stats-grid" id="statsGrid"></div>

      <div class="chart-container">
        <div class="chart-header">
          <span class="chart-title">Progress Over Time</span>
          <div style="display:flex;gap:.5rem;align-items:center">
            <div class="legend">
              <span class="legend-item"><span class="legend-dot" style="background:var(--accent-violet-light)"></span>XP</span>
              <span class="legend-item"><span class="legend-dot" style="background:var(--accent-cyan)"></span>Rating</span>
            </div>
            <div class="pill-group" id="daysPills">
              <button class="pill active" data-days="7">7d</button>
              <button class="pill" data-days="30">30d</button>
              <button class="pill" data-days="90">90d</button>
            </div>
          </div>
        </div>
        <canvas id="profileChart"></canvas>
      </div>

      <div id="platformStats" style="margin-top:1.5rem"></div>
    </div>

    <div id="profileEmpty" class="state-msg" style="display:none">
      <span class="state-icon">🔍</span>
      <span class="state-text" id="emptyMsg">No user found.</span>
    </div>
  `

  let currentUserId = null
  let currentUser = null
  let currentDays = 7
  let currentPlatform = 'codeforces'
  const profileResult = el.querySelector('#profileResult')
  const profileEmpty = el.querySelector('#profileEmpty')

  function setEmptyMessage(message) {
    profileResult.style.display = 'none'
    profileEmpty.style.display = 'flex'
    el.querySelector('#emptyMsg').textContent = message
  }

  function clearEmpty() {
    profileEmpty.style.display = 'none'
  }

  async function loadUserProfile(userFetcher) {
    profileResult.style.display = 'none'
    clearEmpty()

    try {
      const user = await userFetcher()
      currentUser = user
      currentUserId = user.id
      currentPlatform = 'codeforces'

      el.querySelectorAll('[data-platform]').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.platform === 'codeforces')
      })

      const analytics = await api.analytics(user.id, 'codeforces').catch(() => null)
      profileResult.style.display = 'block'
      renderStats(el, user, analytics)
      await loadChart(el, currentUserId, currentDays)
      return { ok: true }
    } catch (err) {
      setEmptyMessage(err.message.includes('404') ? 'User not found.' : `Error: ${err.message}`)
      return { ok: false, error: err }
    }
  }

  if (isSelfPage) {
    const discordInput = el.querySelector('#discordInput')
    const saveSessionBtn = el.querySelector('#saveSessionBtn')
    const logoutBtn = el.querySelector('#logoutBtn')
    const sessionHint = el.querySelector('#sessionHint')

    function refreshSessionHint(discordId) {
      sessionHint.textContent = discordId
        ? `Signed in as Discord ID: ${discordId}`
        : 'No active session.'
    }

    async function loadSelf(discordId) {
      await loadUserProfile(() => api.profileByDiscordId(discordId))
    }

    const savedDiscordId = localStorage.getItem(SESSION_DISCORD_ID_KEY) || ''
    discordInput.value = savedDiscordId
    refreshSessionHint(savedDiscordId)

    if (savedDiscordId) {
      loadSelf(savedDiscordId)
    } else {
      setEmptyMessage('Enter your Discord ID above and hit Sign In to load your profile.')
    }

    discordInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') saveSessionBtn.click()
    })

    saveSessionBtn.addEventListener('click', async () => {
      const discordId = discordInput.value.trim()
      if (!discordId) {
        setEmptyMessage('Please enter your Discord ID.')
        return
      }

      saveSessionBtn.disabled = true
      saveSessionBtn.textContent = 'Signing In…'
      localStorage.setItem(SESSION_DISCORD_ID_KEY, discordId)
      refreshSessionHint(discordId)

      await loadSelf(discordId)

      saveSessionBtn.disabled = false
      saveSessionBtn.textContent = 'Sign In'
    })

    logoutBtn.addEventListener('click', () => {
      localStorage.removeItem(SESSION_DISCORD_ID_KEY)
      discordInput.value = ''
      currentUser = null
      currentUserId = null
      profileResult.style.display = 'none'
      refreshSessionHint('')
      setEmptyMessage('Session cleared. Sign in to load your profile again.')
    })
  } else {
    const handleInput = el.querySelector('#handleInput')
    const loadBtn = el.querySelector('#loadBtn')

    // Enter key
    handleInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') loadBtn.click()
    })

    loadBtn.addEventListener('click', async () => {
      const handle = handleInput.value.trim()
      if (!handle) return

      loadBtn.disabled = true
      loadBtn.textContent = 'Loading…'
      const result = await loadUserProfile(() => api.profileByHandle(handle))
      if (!result.ok && result.error?.message?.includes('404')) {
        setEmptyMessage(`No user found for handle "${handle}".`)
      }
      loadBtn.disabled = false
      loadBtn.textContent = 'Load Profile'
    })

    setEmptyMessage('Search for a Codeforces handle to view a profile.')
  }

  // Platform tabs
  el.querySelectorAll('[data-platform]').forEach(btn => {
    btn.addEventListener('click', async () => {
      if (!currentUserId || !currentUser) return
      el.querySelectorAll('[data-platform]').forEach(b => b.classList.remove('active'))
      btn.classList.add('active')
      currentPlatform = btn.dataset.platform

      try {
        const analytics = await api.analytics(currentUserId, currentPlatform)
        renderStats(el, currentUser, analytics)
        await loadChart(el, currentUserId, currentDays)
      } catch (err) {
        showToast(err.message)
      }
    })
  })

  // Days pills
  el.querySelectorAll('[data-days]').forEach(btn => {
    btn.addEventListener('click', async () => {
      if (!currentUserId) return
      el.querySelectorAll('[data-days]').forEach(b => b.classList.remove('active'))
      btn.classList.add('active')
      currentDays = parseInt(btn.dataset.days)
      await loadChart(el, currentUserId, currentDays)
    })
  })

  return el
}

function renderStats(el, user, analytics) {
  const grid = el.querySelector('#statsGrid')
  const solved = analytics?.solved_count ?? '—'
  const streak = analytics?.streak ?? user.current_streak ?? 0

  grid.innerHTML = `
    <div class="stat-card" style="--accent-color:var(--accent-violet)">
      <div class="stat-card-icon">⚡</div>
      <div class="stat-card-label">XP</div>
      <div class="stat-card-value">${user.xp.toLocaleString()}</div>
    </div>
    <div class="stat-card" style="--accent-color:var(--accent-cyan)">
      <div class="stat-card-icon">📈</div>
      <div class="stat-card-label">Rating</div>
      <div class="stat-card-value">${user.rating.toLocaleString()}</div>
    </div>
    <div class="stat-card" style="--accent-color:var(--accent-green)">
      <div class="stat-card-icon">🏅</div>
      <div class="stat-card-label">Level</div>
      <div class="stat-card-value">${user.level}</div>
    </div>
    <div class="stat-card" style="--accent-color:var(--accent-gold)">
      <div class="stat-card-icon">🔥</div>
      <div class="stat-card-label">Streak</div>
      <div class="stat-card-value">${streak}<span style="font-size:1rem;font-weight:500;color:var(--text-muted)">d</span></div>
    </div>
  `

  // Extra platform info
  const extra = el.querySelector('#platformStats')
  if (analytics) {
    extra.innerHTML = `
      <div class="glass-card" style="padding:1.25rem 1.5rem;display:flex;gap:2rem;flex-wrap:wrap">
        <div>
          <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:.08em;color:var(--text-muted);margin-bottom:.25rem">Solved</div>
          <div style="font-size:1.5rem;font-weight:700;color:var(--accent-green)">${solved}</div>
        </div>
        <div>
          <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:.08em;color:var(--text-muted);margin-bottom:.25rem">Handle</div>
          <div style="font-size:1.1rem;font-weight:600">${escHtml(user.cf_handle)}</div>
        </div>
        <div>
          <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:.08em;color:var(--text-muted);margin-bottom:.25rem">Longest Streak</div>
          <div style="font-size:1.1rem;font-weight:600;color:var(--accent-gold)">${user.longest_streak}d</div>
        </div>
      </div>
    `
  } else {
    extra.innerHTML = ''
  }
}

async function loadChart(el, userId, days) {
  const canvas = el.querySelector('#profileChart')
  if (!canvas) return

  const VIOLET = '#a78bfa'
  const CYAN = '#06b6d4'

  try {
    const [xpData, ratingData] = await Promise.all([
      api.timeseries(userId, 'xp', days),
      api.timeseries(userId, 'rating', days),
    ])

    if (chartInstance) {
      chartInstance.destroy()
      chartInstance = null
    }

    const labels = mergeLabels(
      xpData.points.map(p => p.day),
      ratingData.points.map(p => p.day),
    )

    const xpMap = Object.fromEntries(xpData.points.map(p => [p.day, p.value]))
    const ratingMap = Object.fromEntries(ratingData.points.map(p => [p.day, p.value]))

    chartInstance = new Chart(canvas, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'XP',
            data: labels.map(d => xpMap[d] ?? null),
            borderColor: VIOLET,
            backgroundColor: hexToRgba(VIOLET, 0.08),
            fill: true,
            tension: 0.4,
            pointRadius: 3,
            pointHoverRadius: 6,
            pointBackgroundColor: VIOLET,
            yAxisID: 'y',
          },
          {
            label: 'Rating',
            data: labels.map(d => ratingMap[d] ?? null),
            borderColor: CYAN,
            backgroundColor: hexToRgba(CYAN, 0.06),
            fill: true,
            tension: 0.4,
            pointRadius: 3,
            pointHoverRadius: 6,
            pointBackgroundColor: CYAN,
            yAxisID: 'y2',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        interaction: { mode: 'index', intersect: false },
        animation: { duration: 600, easing: 'easeInOutQuart' },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0f0f1c',
            borderColor: 'rgba(124,58,237,0.3)',
            borderWidth: 1,
            titleColor: '#f1f0ff',
            bodyColor: '#9b97c4',
            padding: 12,
          },
        },
        scales: {
          x: {
            grid: { color: 'rgba(255,255,255,0.04)' },
            ticks: {
              color: '#4e4a6a',
              font: { family: 'Outfit', size: 11 },
              maxTicksLimit: 8,
            },
          },
          y: {
            position: 'left',
            grid: { color: 'rgba(167,139,250,0.07)' },
            ticks: { color: VIOLET, font: { family: 'Outfit', size: 11 } },
          },
          y2: {
            position: 'right',
            grid: { display: false },
            ticks: { color: CYAN, font: { family: 'Outfit', size: 11 } },
          },
        },
      },
    })
  } catch (err) {
    // chart data may be empty — show empty state gracefully  
    if (chartInstance) { chartInstance.destroy(); chartInstance = null }
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.fillStyle = '#4e4a6a'
    ctx.font = '14px Outfit'
    ctx.textAlign = 'center'
    ctx.fillText('No time-series data yet', canvas.width / 2, canvas.height / 2)
  }
}

function mergeLabels(...arrays) {
  const set = new Set(arrays.flat())
  return [...set].sort()
}

function hexToRgba(hex, a) {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r},${g},${b},${a})`
}

function escHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function showToast(msg) {
  const t = document.createElement('div')
  t.className = 'toast'
  t.textContent = msg
  document.body.appendChild(t)
  setTimeout(() => t.remove(), 3500)
}
