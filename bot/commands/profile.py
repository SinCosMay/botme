import discord

from bot.services.backend_client import BackendClient


async def run(client: BackendClient, discord_id: str) -> discord.Embed:
    data = await client.profile(discord_id)
    embed = discord.Embed(
        title=f"{data['cf_handle']} - Profile",
        color=discord.Color.blurple(),
    )
    embed.add_field(name="Level", value=str(data["level"]), inline=True)
    embed.add_field(name="XP", value=f"{data['xp']:,}", inline=True)
    embed.add_field(name="Rating", value=str(data["rating"]), inline=True)
    embed.add_field(name="Current Streak", value=f"{data['current_streak']} day(s)", inline=True)
    embed.add_field(name="Longest Streak", value=f"{data['longest_streak']} day(s)", inline=True)
    embed.add_field(name="Linked Handle", value=data["cf_handle"], inline=True)
    embed.set_footer(text="Float Competitive Profile")
    return embed
