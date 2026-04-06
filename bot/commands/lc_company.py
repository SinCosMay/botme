import discord

from bot.config import settings
from bot.services.backend_client import BackendClient
from bot.services.leetcode_company_source import LeetCodeSourceError, pick_random_company_question


async def run(
    client: BackendClient,  # kept for call signature compatibility
    discord_id: str,  # reserved for future persistence hook
    company: str,
    topic: str | None = None,
    difficulty: str | None = None,
) -> discord.Embed:
    _ = client
    _ = discord_id
    try:
        question = await pick_random_company_question(
            repo=settings.LEETCODE_COMPANY_REPO,
            company=company,
            topic=topic,
            difficulty=difficulty,
        )
    except LeetCodeSourceError as exc:
        return discord.Embed(
            title="Float LeetCode Assignment",
            description=f"Could not fetch question: {exc}",
            color=discord.Color.red(),
        )

    topics_preview = ", ".join(question.topics[:4]) if question.topics else "N/A"
    if len(question.topics) > 4:
        topics_preview += ", ..."

    embed = discord.Embed(
        title="Float LeetCode Assignment",
        description=f"**{question.title}**\n{question.link}",
        color=discord.Color.teal(),
    )
    embed.add_field(name="Company", value=question.company, inline=True)
    embed.add_field(name="Difficulty", value=question.difficulty, inline=True)
    embed.add_field(name="Topic Match", value=topic or "any", inline=True)
    embed.add_field(name="Frequency", value=question.frequency or "N/A", inline=True)
    embed.add_field(name="Acceptance", value=question.acceptance_rate or "N/A", inline=True)
    embed.add_field(name="Topics", value=topics_preview, inline=False)
    return embed
