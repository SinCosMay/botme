from bot.services.backend_client import BackendClient


async def run(client: BackendClient, discord_id: str, cf_handle: str) -> str:
    data = await client.register(discord_id, cf_handle)
    return f"Registered {data['cf_handle']} with XP {data['xp']} and rating {data['rating']}"
