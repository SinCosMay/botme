import discord

from bot.services.backend_client import BackendClient


async def run(
    client: BackendClient,
    discord_id: str,
    company: str,
    topic: str | None = None,
    difficulty: str | None = None,
) -> discord.Embed:
    data = await client.assign_leetcode(discord_id, company, difficulty)

    embed = discord.Embed(
        title="Float LeetCode Assignment",
        description=f"**{data['name']}**\n{data['url']}",
        color=discord.Color.teal(),
    )
    embed.add_field(name="Company", value=company, inline=True)
    embed.add_field(name="Difficulty", value=difficulty or "any", inline=True)
    embed.add_field(name="Topic Match", value=topic or "any", inline=True)

    tags = data.get("tags") or []
    if tags:
        embed.add_field(name="Tags", value=", ".join(tags[:6]), inline=False)

    if topic:
        embed.set_footer(text="Topic filtering for /lc_company is best-effort and may depend on dataset tags.")
    return embed
