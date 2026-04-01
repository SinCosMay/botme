from bot.services.backend_client import BackendClient


async def run(client: BackendClient, discord_id: str, slug: str, proof_url: str | None = None) -> str:
    data = await client.mark_lc_solved(discord_id, slug, proof_url)
    return f"LeetCode solve status: {data['status']}"
