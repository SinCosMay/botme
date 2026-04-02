import './style.css'
import { homePage } from './pages/home.js'
import { leaderboardPage } from './pages/leaderboard.js'
import { profilePage } from './pages/profile.js'

const routes = {
  '/': homePage,
  '/leaderboard': leaderboardPage,
  '/profile': profilePage,
}

const content = document.getElementById('page-content')

function getHash() {
  // strip the leading #
  const h = window.location.hash.slice(1) || '/'
  return h
}

function navigate(path) {
  window.location.hash = path
}

function render() {
  const path = getHash()
  const pageFactory = routes[path] || routes['/']

  // Update nav active state
  document.querySelectorAll('.nav-link[data-link]').forEach(link => {
    const href = link.getAttribute('href').replace('#', '')
    link.classList.toggle('active', href === path || (path === '/' && href === '#/'))
  })

  // Mount page
  content.innerHTML = ''
  const page = pageFactory()
  content.appendChild(page)

  // Scroll to top
  window.scrollTo(0, 0)
}

// Intercept all [data-link] clicks for SPA navigation
document.addEventListener('click', e => {
  const target = e.target.closest('[data-link]')
  if (!target) return
  const href = target.getAttribute('href')
  if (href && href.startsWith('#')) {
    e.preventDefault()
    window.location.hash = href.slice(1)
  }
})

// Hash-based routing
window.addEventListener('hashchange', render)

// Boot
render()
