from bot.services.backend_client import BackendClient


async def run(client: BackendClient, discord_id: str) -> str:
	data = await client.verify_submission(discord_id)
	status = data.get("status")

	if status == "verified":
		base = (
			f"Verification successful. XP +{data.get('xp_awarded', 0)}, "
			f"rating delta {data.get('rating_delta', 0)}."
		)
		followup_prompt = data.get("followup_prompt")
		followup_question_id = data.get("followup_question_id")
		submission_id = data.get("submission_id")
		if followup_prompt and followup_question_id and submission_id:
			return (
				f"{base}\nFollow-up: {followup_prompt}\n"
				f"Use /followup with submission_id={submission_id} and question_id={followup_question_id}."
			)
		return base

	return data.get("message", "No accepted submission found yet.")
