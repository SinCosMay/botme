import discord
from discord import app_commands
from discord.ext import commands

from bot.config import settings
from bot.services.backend_client import BackendClient

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
        data = await client.register(str(interaction.user.id), cf_handle)
        await interaction.followup.send(f"Registered {data['cf_handle']} successfully")
    except Exception as exc:  # pragma: no cover
        await interaction.followup.send(f"Register failed: {exc}")


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
        data = await client.assign_problem(
            str(interaction.user.id),
            mode=mode,
            tag=tag,
            min_rating=min_rating,
            max_rating=max_rating,
        )
        await interaction.followup.send(f"Assigned {data['name']} -> {data['url']}")
    except Exception as exc:  # pragma: no cover
        await interaction.followup.send(f"Assignment failed: {exc}")


@bot.tree.command(name="lc_company", description="Get a LeetCode company-wise problem")
@app_commands.describe(company="Company name", difficulty="easy|medium|hard")
async def lc_company(interaction: discord.Interaction, company: str, difficulty: str | None = None) -> None:
    await interaction.response.defer(thinking=True)
    try:
        data = await client.assign_leetcode(str(interaction.user.id), company, difficulty)
        await interaction.followup.send(f"LeetCode assigned {data['name']} -> {data['url']}")
    except Exception as exc:  # pragma: no cover
        await interaction.followup.send(f"LeetCode assign failed: {exc}")


@bot.tree.command(name="lc_solved", description="Mark assigned LeetCode problem solved")
@app_commands.describe(slug="LeetCode slug", proof_url="Optional proof link")
async def lc_solved(interaction: discord.Interaction, slug: str, proof_url: str | None = None) -> None:
    await interaction.response.defer(thinking=True)
    try:
        data = await client.mark_lc_solved(str(interaction.user.id), slug, proof_url)
        await interaction.followup.send(f"Solve recorded: {data['status']}")
    except Exception as exc:  # pragma: no cover
        await interaction.followup.send(f"LeetCode solve failed: {exc}")


@bot.tree.command(name="solved", description="Verify your latest Codeforces assignment")
async def solved(interaction: discord.Interaction) -> None:
    await interaction.response.defer(thinking=True)
    try:
        data = await client.verify_submission(str(interaction.user.id))
        await interaction.followup.send(
            (
                f"Verification: {data['status']} | XP +{data['xp_awarded']} "
                f"| Rating Delta {data['rating_delta']}"
            )
        )
    except Exception as exc:  # pragma: no cover
        await interaction.followup.send(f"Verification failed: {exc}")


@bot.tree.command(name="profile", description="Show your current profile stats")
async def profile(interaction: discord.Interaction) -> None:
    await interaction.response.defer(thinking=True)
    try:
        data = await client.profile(str(interaction.user.id))
        await interaction.followup.send(
            (
                f"XP: {data['xp']} | Rating: {data['rating']} | "
                f"Level: {data['level']} | Streak: {data['current_streak']}"
            )
        )
    except Exception as exc:  # pragma: no cover
        await interaction.followup.send(f"Profile failed: {exc}")


if __name__ == "__main__":
    if not settings.DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN is not set")
    bot.run(settings.DISCORD_TOKEN)
