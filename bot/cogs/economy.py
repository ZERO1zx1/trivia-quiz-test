import discord
from discord import app_commands
from discord.ext import commands
from backend.models import User
from bot.main import app, db

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="View your TriviaVerse profile and stats.")
    async def profile(self, interaction: discord.Interaction):
        with app.app_context():
            user = User.query.filter_by(discord_id=str(interaction.user.id)).first()
            
            if not user:
                await interaction.response.send_message("You haven't linked your TriviaVerse account yet! Visit the website to link.", ephemeral=True)
                return

            embed = discord.Embed(title=f"{interaction.user.name}'s Profile", color=0x5865F2)
            embed.add_field(name="Level", value=str(user.level), inline=True)
            embed.add_field(name="XP", value=str(user.xp), inline=True)
            embed.add_field(name="Coins", value=f"🪙 {user.coins}", inline=True)
            
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))