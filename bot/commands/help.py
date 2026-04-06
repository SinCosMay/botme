import discord


def run() -> discord.Embed:
	embed = discord.Embed(
		title="Float Command Guide",
		description="Practice coding consistently, track stats, and compete on the leaderboard.",
		color=discord.Color.purple(),
	)
	embed.add_field(name="Registration", value="`/register <cf_handle>`", inline=False)
	embed.add_field(name="Codeforces", value="`/problem`\n`/solved`\n`/followup`", inline=True)
	embed.add_field(name="LeetCode", value="`/lc_company`\n`/lc_solved`", inline=True)
	embed.add_field(name="Stats", value="`/profile`\n`/leaderboard`", inline=True)
	embed.add_field(name="Utility", value="`/ping`\n`/help`", inline=False)
	embed.set_footer(text="Tip: Use /leaderboard metric:xp or metric:rating")
	return embed
