export function homePage() {
  const el = document.createElement('div')
  el.innerHTML = `
    <section class="hero">
      <div class="hero-bg"></div>

      <div class="hero-content">
        <div class="hero-label">Codeforces &nbsp;·&nbsp; LeetCode &nbsp;·&nbsp; Discord</div>

        <h1 class="hero-title">
          Code and <span class="word-float">Float</span>
        </h1>

        <p class="hero-sub">
          Float tracks every solve, awards XP, handles follow-up questions,
          and ranks you on a live leaderboard — all from Discord.
        </p>

        <div class="hero-actions">
          <a href="#/leaderboard" class="btn-primary" data-link>
            Leaderboard &rarr;
          </a>
          <a href="#/search" class="btn-ghost" data-link>
            Search Profiles
          </a>
        </div>
      </div>

      <div class="hero-stats">
        <div class="hs-item">
          <div class="hs-num" id="lbCount">—</div>
          <div class="hs-label">Ranked Users</div>
        </div>
        <div class="hs-item">
          <div class="hs-num">2</div>
          <div class="hs-label">Platforms</div>
        </div>
        <div class="hs-item">
          <div class="hs-num">∞</div>
          <div class="hs-label">Problems</div>
        </div>
      </div>
    </section>

    <div class="features-section">
      <div class="section-label">What Float does</div>
      <div class="section-title">Everything you need to<br>stay sharp and ranked</div>

      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-mark"></div>
          <div class="feature-title">Competitive Track</div>
          <div class="feature-desc">
            Solve Codeforces problems by tag, rating, or random. The backend verifies
            your actual submission via the CF API.
          </div>
        </div>
        <div class="feature-card">
          <div class="feature-mark"></div>
          <div class="feature-title">XP &amp; Rating</div>
          <div class="feature-desc">
            Earn XP for every solve. Your rating evolves based on problem
            difficulty, so each session counts.
          </div>
        </div>
        <div class="feature-card">
          <div class="feature-mark"></div>
          <div class="feature-title">Follow-up Engine</div>
          <div class="feature-desc">
            After each solve, answer a concept question for bonus XP —
            reinforcing exactly what you learned.
          </div>
        </div>
        <div class="feature-card">
          <div class="feature-mark"></div>
          <div class="feature-title">Streak Tracking</div>
          <div class="feature-desc">
            Maintain daily solve streaks. Float reminds you before
            your streak breaks.
          </div>
        </div>
        <div class="feature-card">
          <div class="feature-mark"></div>
          <div class="feature-title">LeetCode Company Prep</div>
          <div class="feature-desc">
            Practice company-tagged LeetCode problems separately — perfect for
            interviews, without affecting your CF score.
          </div>
        </div>
        <div class="feature-card">
          <div class="feature-mark"></div>
          <div class="feature-title">Analytics Dashboard</div>
          <div class="feature-desc">
            View rating and XP trends over time, compare with peers,
            and drill into your full solve history.
          </div>
        </div>
      </div>
    </div>
  `

  // Load leaderboard user count
  import('/src/api.js').then(({ api }) => {
    api.leaderboard('xp', 1, 1)
      .then(data => {
        const counter = document.getElementById('lbCount')
        if (counter) counter.textContent = data.total || 0
      })
      .catch(() => { })
  })

  return el
}
