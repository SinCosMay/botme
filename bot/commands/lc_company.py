import discord

from bot.config import settings
from bot.services.backend_client import BackendClient, BackendClientError
from bot.services.leetcode_company_source import LeetCodeSourceError, pick_random_company_question


async def run(
    client: BackendClient,
    discord_id: str,
    company: str,
    topic: str | None = None,
    difficulty: str | None = None,
) -> discord.Embed:
    try:
        data = await client.assign_leetcode(discord_id, company, difficulty)

        embed = discord.Embed(
            title="Float LeetCode Assignment",
            description=f"**{data['name']}**\n{data['url']}",
            color=discord.Color.teal(),
        )
        embed.add_field(name="Company", value=company, inline=True)
        embed.add_field(name="Difficulty", value=difficulty or "any", inline=True)
        embed.add_field(name="Topic Match", value=topic or "any", inline=True)

        tags = data.get("tags") or []
        if tags:
            embed.add_field(name="Tags", value=", ".join(tags[:6]), inline=False)

        if topic:
            embed.set_footer(text="Topic filtering for /lc_company is best-effort and may depend on dataset tags.")
        return embed
    except BackendClientError as exc:
        if exc.status_code in {404, 400} and "No matching LeetCode problems available" in exc.message:
            try:
                question = await pick_random_company_question(
                    repo=settings.LEETCODE_COMPANY_REPO,
                    company=company,
                    topic=topic,
                    difficulty=difficulty,
                )
            except LeetCodeSourceError as source_exc:
                return discord.Embed(
                    title="Float LeetCode Assignment",
                    description=f"No matching LeetCode problems available: {source_exc}",
                    color=discord.Color.red(),
                )

            topics_preview = ", ".join(question.topics[:6]) if question.topics else "N/A"
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
            embed.set_footer(text="Fallback source: company-wise GitHub dataset")
            return embed

        return discord.Embed(
            title="Float LeetCode Assignment",
            description=f"LeetCode assign failed: {exc.message}",
            color=discord.Color.red(),
        )
