from bot.services.backend_client import BackendClient


async def run(client: BackendClient, submission_id: str, question_id: str, answer: str) -> str:
    data = await client.answer_followup(submission_id, question_id, answer)
    correctness = "correct" if data.get("is_correct") else "incorrect"
    return (
        f"Follow-up {correctness}. Bonus XP +{data.get('awarded_xp', 0)}. "
        f"Now XP={data.get('user_xp', 0)}, level={data.get('user_level', 1)}."
    )
