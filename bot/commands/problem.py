from bot.services.backend_client import BackendClient


async def run(
    client: BackendClient,
    discord_id: str,
    mode: str = "random",
    tag: str | None = None,
    min_rating: int | None = None,
    max_rating: int | None = None,
) -> str:
    data = await client.assign_problem(
        discord_id,
        mode=mode,
        tag=tag,
        min_rating=min_rating,
        max_rating=max_rating,
    )
    rating = data.get("rating")
    tags = data.get("tags") or []
    rating_text = f" | rating: {rating}" if rating is not None else ""
    tags_text = f" | tags: {', '.join(tags[:5])}" if tags else ""
    return f"Assigned: {data['name']} ({data['url']}){rating_text}{tags_text}"
