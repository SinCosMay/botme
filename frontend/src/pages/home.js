export function homePage() {
  const el = document.createElement('div')
  el.innerHTML = `
    <section class="hero">
      <canvas class="hero-canvas" id="heroCanvas"></canvas>

      <span class="hero-eyebrow">Discord × Codeforces × LeetCode</span>

      <h1 class="hero-title">
        Level up your<br/>
        <span class="gradient-word">Competitive Skills</span>
      </h1>

      <p class="hero-sub">
        BotMe tracks your Codeforces solves, awards XP &amp; rating, handles
        follow-up concept questions, and ranks you on a live leaderboard —
        all through Discord.
      </p>

      <div class="hero-actions">
        <a href="#/leaderboard" class="btn-primary" data-link>
          🏆 Leaderboard
        </a>
        <a href="#/my-profile" class="btn-ghost" data-link>
          👤 My Profile
        </a>
        <a href="#/search" class="btn-ghost" data-link>
          🔎 Search Profiles
        </a>
      </div>

      <div class="stats-strip">
        <div class="stat-item">
          <div class="stat-number" id="lbCount">—</div>
          <div class="stat-label">Ranked Users</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">2</div>
          <div class="stat-label">Platforms</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">∞</div>
          <div class="stat-label">Problems</div>
        </div>
      </div>
    </section>

    <div class="features">
      <div class="feature-card">
        <span class="feature-icon">⚔️</span>
        <div class="feature-title">Competitive Track</div>
        <div class="feature-desc">
          Solve Codeforces problems by tag, rating, or random. Backend verifies
          your actual submission via the CF API.
        </div>
      </div>
      <div class="feature-card">
        <span class="feature-icon">📈</span>
        <div class="feature-title">XP &amp; Rating</div>
        <div class="feature-desc">
          Earn XP for every solve. Your rating evolves based on problem
          difficulty. Level up and climb the leaderboard.
        </div>
      </div>
      <div class="feature-card">
        <span class="feature-icon">🧠</span>
        <div class="feature-title">Follow-up Engine</div>
        <div class="feature-desc">
          After each solve, answer a concept question for bonus XP —
          reinforcing what you learned.
        </div>
      </div>
      <div class="feature-card">
        <span class="feature-icon">🔥</span>
        <div class="feature-title">Streak Tracking</div>
        <div class="feature-desc">
          Maintain daily solve streaks. The bot reminds you before your
          streak breaks.
        </div>
      </div>
      <div class="feature-card">
        <span class="feature-icon">🏢</span>
        <div class="feature-title">LeetCode Company-Wise</div>
        <div class="feature-desc">
          Practice company-tagged LeetCode problems separately — perfect for
          interview prep without affecting your CF score.
        </div>
      </div>
      <div class="feature-card">
        <span class="feature-icon">📊</span>
        <div class="feature-title">Analytics Dashboard</div>
        <div class="feature-desc">
          This page. View rating &amp; XP trends, compare with peers,
          and drill into your solve history.
        </div>
      </div>
    </div>
  `

  // Animate hero canvas
  requestAnimationFrame(() => initHeroCanvas(el.querySelector('#heroCanvas')))

  // Load leaderboard count
  import('/src/api.js').then(({ api }) => {
    api.leaderboard('xp', 1, 1)
      .then(data => {
        const el2 = document.getElementById('lbCount')
        if (el2) el2.textContent = data.total || 0
      })
      .catch(() => {})
  })

  return el
}

function initHeroCanvas(canvas) {
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const W = canvas.width = canvas.offsetWidth
  const H = canvas.height = canvas.offsetHeight

  const PARTICLE_COUNT = 60
  const particles = Array.from({ length: PARTICLE_COUNT }, () => ({
    x: Math.random() * W,
    y: Math.random() * H,
    r: Math.random() * 1.5 + 0.5,
    vx: (Math.random() - 0.5) * 0.35,
    vy: (Math.random() - 0.5) * 0.35,
    opacity: Math.random() * 0.5 + 0.1,
  }))

  let frame
  function draw() {
    ctx.clearRect(0, 0, W, H)

    // Gradient background glow
    const grad = ctx.createRadialGradient(W * 0.5, H * 0.4, 0, W * 0.5, H * 0.4, H * 0.7)
    grad.addColorStop(0, 'rgba(124, 58, 237, 0.08)')
    grad.addColorStop(0.5, 'rgba(6, 182, 212, 0.04)')
    grad.addColorStop(1, 'transparent')
    ctx.fillStyle = grad
    ctx.fillRect(0, 0, W, H)

    for (const p of particles) {
      p.x += p.vx
      p.y += p.vy
      if (p.x < 0) p.x = W
      if (p.x > W) p.x = 0
      if (p.y < 0) p.y = H
      if (p.y > H) p.y = 0

      ctx.beginPath()
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(167, 139, 250, ${p.opacity})`
      ctx.fill()
    }

    // Connecting lines
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x
        const dy = particles[i].y - particles[j].y
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < 100) {
          ctx.beginPath()
          ctx.moveTo(particles[i].x, particles[i].y)
          ctx.lineTo(particles[j].x, particles[j].y)
          ctx.strokeStyle = `rgba(124, 58, 237, ${(1 - dist / 100) * 0.12})`
          ctx.lineWidth = 0.8
          ctx.stroke()
        }
      }
    }

    frame = requestAnimationFrame(draw)
  }

  draw()

  // Cleanup observer
  const observer = new IntersectionObserver(entries => {
    if (!entries[0].isIntersecting) cancelAnimationFrame(frame)
  })
  observer.observe(canvas)
}
