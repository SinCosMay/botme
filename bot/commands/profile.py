from bot.services.backend_client import BackendClient


async def run(client: BackendClient, discord_id: str) -> str:
    data = await client.profile(discord_id)
    return (
        f"Profile -> XP: {data['xp']}, rating: {data['rating']}, "
        f"level: {data['level']}, streak: {data['current_streak']}"
    )
