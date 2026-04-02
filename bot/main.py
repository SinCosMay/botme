import discord
from discord import app_commands
from discord.ext import commands

from bot.commands import lc_company as lc_company_cmd
from bot.commands import lc_solved as lc_solved_cmd
from bot.commands import followup as followup_cmd
from bot.commands import leaderboard as leaderboard_cmd
from bot.commands import problem as problem_cmd
from bot.commands import profile as profile_cmd
from bot.commands import register as register_cmd
from bot.commands import solved as solved_cmd
from bot.config import settings
from bot.services.backend_client import BackendClient, BackendClientError

client = BackendClient(settings.API_URL)
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

GUILD_ID = 740102523716763668

@bot.event
async def on_ready() -> None:
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    synced = await bot.tree.sync(guild=guild)

    print(f"Synced {len(synced)} commands to guild")
    print(f"Bot ready as {bot.user}")


@bot.tree.command(name="register", description="Link Discord ID with Codeforces handle")
@app_commands.describe(cf_handle="Your Codeforces handle")
async def register(interaction: discord.Interaction, cf_handle: str) -> None:
    await interaction.response.defer(thinking=True)
    try:
        message = await register_cmd.run(client, str(interaction.user.id), cf_handle)
        await interaction.followup.send(message)
    except BackendClientError as exc:  # pragma: no cover
        await interaction.followup.send(f"Register failed: {exc.message}")


@bot.tree.command(name="problem", description="Get a Codeforces problem")
@app_commands.describe(
    mode="random|topic|rating",
    topic="topic tag (example: dp, greedy)",
    min_rating="minimum rating",
    max_rating="maximum rating",
)
async def problem(
    interaction: discord.Interaction,
    mode: str = "random",
    topic: str | None = None,
    min_rating: int | None = None,
    max_rating: int | None = None,
) -> None:
    await interaction.response.defer(thinking=True)
    try:
        resolved_mode = (mode or "random").strip().lower()
        if topic and resolved_mode == "random":
            resolved_mode = "topic"
        elif (min_rating is not None or max_rating is not None) and resolved_mode == "random":
            resolved_mode = "rating"

        if min_rating is not None and max_rating is not None and min_rating > max_rating:
            await interaction.followup.send("Assignment failed: min_rating cannot be greater than max_rating")
            return

        message = await problem_cmd.run(
            client,
            str(interaction.user.id),
            mode=resolved_mode,
            tag=topic,
            min_rating=min_rating,
            max_rating=max_rating,
        )
        await interaction.followup.send(message)
    except BackendClientError as exc:  # pragma: no cover
        await interaction.followup.send(f"Assignment failed: {exc.message}")


@bot.tree.command(name="lc_company", description="Get a LeetCode company-wise problem")
@app_commands.describe(company="Company name", difficulty="easy|medium|hard")
async def lc_company(interaction: discord.Interaction, company: str, difficulty: str | None = None) -> None:
    await interaction.response.defer(thinking=True)
    try:
        message = await lc_company_cmd.run(client, str(interaction.user.id), company, difficulty)
        await interaction.followup.send(message)
    except BackendClientError as exc:  # pragma: no cover
        await interaction.followup.send(f"LeetCode assign failed: {exc.message}")


@bot.tree.command(name="lc_solved", description="Mark assigned LeetCode problem solved")
@app_commands.describe(slug="LeetCode slug", proof_url="Optional proof link")
async def lc_solved(interaction: discord.Interaction, slug: str, proof_url: str | None = None) -> None:
    await interaction.response.defer(thinking=True)
    try:
        message = await lc_solved_cmd.run(client, str(interaction.user.id), slug, proof_url)
        await interaction.followup.send(message)
    except BackendClientError as exc:  # pragma: no cover
        await interaction.followup.send(f"LeetCode solve failed: {exc.message}")


@bot.tree.command(name="solved", description="Verify your latest Codeforces assignment")
async def solved(interaction: discord.Interaction) -> None:
    await interaction.response.defer(thinking=True)
    try:
        message = await solved_cmd.run(client, str(interaction.user.id))
        await interaction.followup.send(message)
    except BackendClientError as exc:  # pragma: no cover
        await interaction.followup.send(f"Verification failed: {exc.message}")


@bot.tree.command(name="profile", description="Show your current profile stats")
async def profile(interaction: discord.Interaction) -> None:
    await interaction.response.defer(thinking=True)
    try:
        message = await profile_cmd.run(client, str(interaction.user.id))
        await interaction.followup.send(message)
    except BackendClientError as exc:  # pragma: no cover
        await interaction.followup.send(f"Profile failed: {exc.message}")


@bot.tree.command(name="leaderboard", description="Show top users by XP or rating")
@app_commands.describe(metric="xp|rating", limit="number of rows (1-20)")
async def leaderboard(
    interaction: discord.Interaction,
    metric: str = "xp",
    limit: int = 10,
) -> None:
    await interaction.response.defer(thinking=True)
    try:
        message = await leaderboard_cmd.run(client, metric=metric, limit=max(1, min(limit, 20)))
        await interaction.followup.send(message)
    except BackendClientError as exc:  # pragma: no cover
        await interaction.followup.send(f"Leaderboard failed: {exc.message}")


@bot.tree.command(name="followup", description="Submit follow-up answer for a solved assignment")
@app_commands.describe(submission_id="Submission id from /solved", question_id="Question id from /solved", answer="Your answer")
async def followup(
    interaction: discord.Interaction,
    submission_id: str,
    question_id: str,
    answer: str,
) -> None:
    await interaction.response.defer(thinking=True)
    try:
        message = await followup_cmd.run(client, submission_id=submission_id, question_id=question_id, answer=answer)
        await interaction.followup.send(message)
    except BackendClientError as exc:  # pragma: no cover
        await interaction.followup.send(f"Follow-up failed: {exc.message}")


if __name__ == "__main__":
    if not settings.DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN is not set")
    bot.run(settings.DISCORD_TOKEN)
