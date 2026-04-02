from bot.services.backend_client import BackendClient


async def run(client: BackendClient, discord_id: str) -> str:
    data = await client.profile(discord_id)
    return f"LeetCode profile placeholder. Current global XP: {data['xp']}"
