from bot.services.backend_client import BackendClient


async def run(client: BackendClient, metric: str = "xp", limit: int = 10) -> str:
	data = await client.leaderboard(metric=metric, page=1, limit=limit)
	entries = data.get("entries", [])
	if not entries:
		return "No leaderboard entries available yet."

	lines = [f"Leaderboard ({data.get('metric', metric)}):"]
	for row in entries:
		lines.append(
			f"#{row['rank']} {row['cf_handle']} | XP {row['xp']} | Rating {row['rating']} | Lv {row['level']}"
		)
	return "\n".join(lines)
