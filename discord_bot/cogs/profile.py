import discord
from discord.ext import commands
from discord import app_commands

class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="View your TriviaVerse profile")
    @app_commands.describe(user="User to view (optional)")
    async def profile(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user

        embed = discord.Embed(
            title=f"🎮 {target.display_name}'s Profile",
            color=0x5865F2
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Level", value="1 ⭐", inline=True)
        embed.add_field(name="XP", value="0 / 100", inline=True)
        embed.add_field(name="Coins", value="🪙 500", inline=True)
        embed.add_field(name="Wins", value="0", inline=True)
        embed.add_field(name="Games", value="0", inline=True)
        embed.add_field(name="Accuracy", value="0%", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rank", description="Check your leaderboard rank")
    async def rank(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🏆 Your Ranking",
            description="You are unranked. Play some games!",
            color=0xFFD700
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="View global leaderboard")
    @app_commands.describe(period="Time period", limit="Number of players (max 25)")
    @app_commands.choices(period=[
        app_commands.Choice(name="Daily", value="daily"),
        app_commands.Choice(name="Weekly", value="weekly"),
        app_commands.Choice(name="Monthly", value="monthly"),
        app_commands.Choice(name="All Time", value="alltime")
    ])
    async def leaderboard(self, interaction: discord.Interaction, period: str = "alltime", limit: int = 10):
        limit = min(max(limit, 3), 25)

        embed = discord.Embed(
            title=f"🏆 {period.title()} Leaderboard",
            color=0xFFD700
        )

        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        for i in range(min(5, limit)):
            embed.add_field(
                name=f"{medals[i]} Player {i+1}",
                value="Score: 0 | Level: 1",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ProfileCog(bot))
