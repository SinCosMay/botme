from bot.services.backend_client import BackendClient


async def run(client: BackendClient, discord_id: str) -> str:
	data = await client.verify_submission(discord_id)
	status = data.get("status")

	if status == "verified":
		return (
			f"Verification successful. XP +{data.get('xp_awarded', 0)}, "
			f"rating delta {data.get('rating_delta', 0)}."
		)

	return data.get("message", "No accepted submission found yet.")
