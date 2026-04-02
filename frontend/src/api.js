const BASE = (import.meta.env.VITE_API_BASE || '/v1').replace(/\/$/, '')

async function apiFetch(path) {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) {
    let detail = res.statusText
    try {
      const payload = await res.json()
      if (payload && typeof payload.detail === 'string') {
        detail = payload.detail
      }
    } catch {
      // keep status text
    }
    throw new Error(`API ${res.status}: ${detail}`)
  }
  return res.json()
}

export const api = {
  /** GET /v1/analytics/leaderboard?metric=xp&page=1&limit=10 */
  leaderboard: (metric = 'xp', page = 1, limit = 10) =>
    apiFetch(`/analytics/leaderboard?metric=${metric}&page=${page}&limit=${limit}`),

  /** GET /v1/users/handle/{cf_handle}/profile */
  profileByHandle: (handle) =>
    apiFetch(`/users/handle/${encodeURIComponent(handle)}/profile`),

  /** GET /v1/users/{discord_id}/profile */
  profileByDiscordId: (discordId) =>
    apiFetch(`/users/${encodeURIComponent(discordId)}/profile`),

  /** GET /v1/analytics/{user_id}?platform=codeforces */
  analytics: (userId, platform = 'codeforces') =>
    apiFetch(`/analytics/${userId}?platform=${platform}`),

  /** GET /v1/analytics/{user_id}/timeseries?metric=xp&days=30 */
  timeseries: (userId, metric = 'xp', days = 30) =>
    apiFetch(`/analytics/${userId}/timeseries?metric=${metric}&days=${days}`),

  /** GET /v1/health */
  health: () => apiFetch('/health'),
}
