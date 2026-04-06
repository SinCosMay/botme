import discord

from bot.services.backend_client import BackendClient


async def run(client: BackendClient, discord_id: str, cf_handle: str) -> discord.Embed:
    data = await client.register(discord_id, cf_handle)
    embed = discord.Embed(
        title="Float Registration Complete",
        description=f"Linked Codeforces handle **{data['cf_handle']}**.",
        color=discord.Color.green(),
    )
    embed.add_field(name="XP", value=f"{data['xp']:,}", inline=True)
    embed.add_field(name="Rating", value=str(data["rating"]), inline=True)
    embed.add_field(name="Level", value=str(data["level"]), inline=True)
    return embed
