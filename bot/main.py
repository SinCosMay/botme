import discord
from discord import app_commands
from discord.ext import commands
import time

from bot.commands import lc_company as lc_company_cmd
from bot.commands import lc_solved as lc_solved_cmd
from bot.commands import followup as followup_cmd
from bot.commands import help as help_cmd
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


def _get_local_command_names() -> list[str]:
    return [cmd.name for cmd in bot.tree.get_commands(guild=None)]


async def _clear_remote_global_commands() -> int:
    app_id = bot.application_id
    if app_id is None:
        app_info = await bot.application_info()
        app_id = app_info.id

    existing_global = await bot.http.get_global_commands(app_id)
    for command in existing_global:
        command_id = int(command["id"])
        await bot.http.delete_global_command(app_id, command_id)
    return len(existing_global)

@bot.event
async def on_ready() -> None:
    local_names = _get_local_command_names()
    if len(local_names) != len(set(local_names)):
        duplicates = sorted({name for name in local_names if local_names.count(name) > 1})
        print(f"Duplicate local slash command names detected: {duplicates}")

    if settings.DISCORD_SYNC_GUILD_ONLY and settings.DISCORD_GUILD_ID:
        guild = discord.Object(id=settings.DISCORD_GUILD_ID)

        # Clear stale remote global registrations to avoid duplicate slash entries.
        if settings.DISCORD_CLEAR_GLOBAL_WHEN_GUILD_SYNC:
            try:
                cleared_count = await _clear_remote_global_commands()
                print(f"Cleared {cleared_count} stale global commands")
            except Exception as exc:  # pragma: no cover
                print(f"Failed to clear stale global commands: {exc}")

        bot.tree.clear_commands(guild=guild)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} commands to guild {settings.DISCORD_GUILD_ID}")
    else:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} global commands")

    print(f"Bot ready as {bot.user}")


@bot.tree.command(name="register", description="Link Discord ID with Codeforces handle")
@app_commands.describe(cf_handle="Your Codeforces handle")
async def register(interaction: discord.Interaction, cf_handle: str) -> None:
    await interaction.response.defer(thinking=True)
    try:
        embed = await register_cmd.run(client, str(interaction.user.id), cf_handle)
        await interaction.followup.send(embed=embed)
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

        embed = await problem_cmd.run(
            client,
            str(interaction.user.id),
            mode=resolved_mode,
            tag=topic,
            min_rating=min_rating,
            max_rating=max_rating,
        )
        await interaction.followup.send(embed=embed)
    except BackendClientError as exc:  # pragma: no cover
        await interaction.followup.send(f"Assignment failed: {exc.message}")


@bot.tree.command(name="lc_company", description="Get a LeetCode company-wise problem from all-time CSV")
@app_commands.describe(
    company="Company name",
    topic="Optional topic to filter (example: graph, dp)",
    difficulty="easy|medium|hard",
)
async def lc_company(
    interaction: discord.Interaction,
    company: str,
    topic: str | None = None,
    difficulty: str | None = None,
) -> None:
    await interaction.response.defer(thinking=True)
    embed = await lc_company_cmd.run(client, str(interaction.user.id), company, topic, difficulty)
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="lc_solved", description="Mark assigned LeetCode problem solved")
@app_commands.describe(slug="LeetCode slug", proof_url="Optional proof link")
async def lc_solved(interaction: discord.Interaction, slug: str, proof_url: str | None = None) -> None:
    await interaction.response.defer(thinking=True)
    try:
        embed = await lc_solved_cmd.run(client, str(interaction.user.id), slug, proof_url)
        await interaction.followup.send(embed=embed)
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
        embed = await profile_cmd.run(client, str(interaction.user.id))
        await interaction.followup.send(embed=embed)
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
        embed = await leaderboard_cmd.run(client, metric=metric, limit=max(1, min(limit, 20)))
        await interaction.followup.send(embed=embed)
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


@bot.tree.command(name="help", description="Show Float commands and what they do")
async def help_command(interaction: discord.Interaction) -> None:
    embed = help_cmd.run()
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction) -> None:
    started = time.perf_counter()
    await interaction.response.defer(thinking=True)
    elapsed_ms = (time.perf_counter() - started) * 1000
    websocket_ms = bot.latency * 1000

    embed = discord.Embed(
        title="Float Ping",
        color=discord.Color.green(),
    )
    embed.add_field(name="Gateway", value=f"{websocket_ms:.2f} ms", inline=True)
    embed.add_field(name="Command", value=f"{elapsed_ms:.2f} ms", inline=True)
    await interaction.followup.send(embed=embed)


if __name__ == "__main__":
    if not settings.DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN is not set")
    bot.run(settings.DISCORD_TOKEN)
