from bot.services.backend_client import BackendClient


async def run(client: BackendClient, discord_id: str, company: str, difficulty: str | None = None) -> str:
    data = await client.assign_leetcode(discord_id, company, difficulty)
    return f"LeetCode assigned: {data['name']} ({data['url']})"
