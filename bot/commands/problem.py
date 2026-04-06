import discord

from bot.services.backend_client import BackendClient


async def run(
    client: BackendClient,
    discord_id: str,
    mode: str = "random",
    tag: str | None = None,
    min_rating: int | None = None,
    max_rating: int | None = None,
) -> discord.Embed:
    data = await client.assign_problem(
        discord_id,
        mode=mode,
        tag=tag,
        min_rating=min_rating,
        max_rating=max_rating,
    )
    rating = data.get("rating")
    tags = data.get("tags") or []
    embed = discord.Embed(
        title="Float Problem Assignment",
        description=f"**{data['name']}**\n{data['url']}",
        color=discord.Color.blue(),
    )
    embed.add_field(name="Platform", value=str(data.get("platform", "codeforces")).title(), inline=True)
    embed.add_field(name="Mode", value=mode.title(), inline=True)
    embed.add_field(name="Rating", value=str(rating) if rating is not None else "N/A", inline=True)
    if tags:
        embed.add_field(name="Tags", value=", ".join(tags[:6]), inline=False)
    return embed
