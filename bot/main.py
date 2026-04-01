import discord
from discord import app_commands
from discord.ext import commands

from bot.commands import lc_company as lc_company_cmd
from bot.commands import lc_solved as lc_solved_cmd
from bot.commands import problem as problem_cmd
from bot.commands import profile as profile_cmd
from bot.commands import register as register_cmd
from bot.commands import solved as solved_cmd
from bot.config import settings
from bot.services.backend_client import BackendClient, BackendClientError

client = BackendClient(settings.API_URL)
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)


@bot.event
async def on_ready() -> None:
    await bot.tree.sync()
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
@app_commands.describe(mode="random|topic|rating", tag="topic tag", min_rating="minimum rating", max_rating="maximum rating")
async def problem(
    interaction: discord.Interaction,
    mode: str = "random",
    tag: str | None = None,
    min_rating: int | None = None,
    max_rating: int | None = None,
) -> None:
    await interaction.response.defer(thinking=True)
    try:
        message = await problem_cmd.run(
            client,
            str(interaction.user.id),
            mode=mode,
            tag=tag,
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


if __name__ == "__main__":
    if not settings.DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN is not set")
    bot.run(settings.DISCORD_TOKEN)
