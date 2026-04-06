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
	metric_key = str(data.get("metric", metric)).strip().lower()
	metric_name = metric_key.upper()

	embed = discord.Embed(
		title=f"Float Leaderboard - {metric_name}",
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
		if metric_key == "rating":
			value_text = f"Rating `{row['rating']}`"
		else:
			value_text = f"XP `{row['xp']:,}`"
		lines.append(f"{prefix} **{row['cf_handle']}**\n{value_text}  |  Lv `{row['level']}`")

	embed.description = "\n".join(lines)
	embed.set_footer(
		text=(
			f"Metric {metric_name} | Showing {len(entries)} | "
			f"Total {data.get('total', len(entries))} | "
			f"Page {data.get('page', 1)}"
		)
	)
	return embed
