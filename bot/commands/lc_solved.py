import discord

from bot.services.backend_client import BackendClient


async def run(client: BackendClient, discord_id: str, slug: str, proof_url: str | None = None) -> discord.Embed:
    data = await client.mark_lc_solved(discord_id, slug, proof_url)
    status = str(data.get("status", "recorded"))
    color = discord.Color.green() if status == "recorded" else discord.Color.orange()
    embed = discord.Embed(
        title="Float LeetCode Progress",
        description=f"Solve status: **{status}**",
        color=color,
    )
    embed.add_field(name="Slug", value=slug, inline=True)
    if proof_url:
        embed.add_field(name="Proof", value=proof_url, inline=False)
    return embed
