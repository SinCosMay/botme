import discord

from bot.services.backend_client import BackendClient


def _rank_prefix(rank: int) -> str:
	if rank == 1:
		return "🥇"
	if rank == 2:
		return "🥈"
	if rank == 3:
		return "🥉"
	return f"#{rank}"


async def run(client: BackendClient, metric: str = "xp", limit: int = 10) -> discord.Embed:
	data = await client.leaderboard(metric=metric, page=1, limit=limit)
	entries = data.get("entries", [])
	metric_name = str(data.get("metric", metric)).upper()

	embed = discord.Embed(
		title=f"BotMe Leaderboard - {metric_name}",
		color=discord.Color.gold(),
	)
	if not entries:
		embed.description = "No leaderboard entries available yet."
		embed.set_footer(text="Try again after users start solving problems")
		return embed

	lines = []
	for row in entries:
		rank = int(row["rank"])
		prefix = _rank_prefix(rank)
		lines.append(
			f"{prefix} **{row['cf_handle']}** - XP `{row['xp']:,}` - Rating `{row['rating']}` - Lv `{row['level']}`"
		)

	embed.description = "\n".join(lines)
	embed.add_field(name="Metric", value=metric_name, inline=True)
	embed.add_field(name="Showing", value=str(len(entries)), inline=True)
	embed.add_field(name="Total Users", value=str(data.get("total", len(entries))), inline=True)
	embed.set_footer(text=f"Page {data.get('page', 1)} | Limit {data.get('limit', limit)}")
	return embed
